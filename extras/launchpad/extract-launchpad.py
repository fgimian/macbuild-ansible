from __future__ import print_function

from collections import defaultdict
import os
import subprocess
import sqlite3
from time import sleep
import yaml


class Types(object):
    ROOT = 1
    FOLDER_ROOT = 2
    PAGE = 3
    APP = 4
    DOWNLOADING_APP = 5
    WIDGET = 6


def build_layout(root, layout_key, parent_mapping, layout):
    for page_id, _, _, _, _ in parent_mapping[root]:
        page_items = []

        for id, type_, app_title, widget_title, group_title in parent_mapping[page_id]:
            if type_ == Types.APP:
                page_items.append(app_title)
            elif type_ == Types.WIDGET:
                page_items.append(widget_title)
            elif type_ == Types.FOLDER_ROOT:
                folder_items = {
                    'folder_title': group_title,
                    'folder_layout': []
                }

                for folder_page_id, _, _, _, _ in parent_mapping[id]:
                    for (
                        folder_item_id, folder_item_type, folder_item_app_title,
                        folder_widget_title, folder_group_title
                    ) in parent_mapping[folder_page_id]:
                        if folder_item_type == Types.APP:
                            folder_items['folder_layout'].append(folder_item_app_title)
                        elif folder_item_type == Types.WIDGET:
                            folder_items['folder_layout'].append(folder_widget_title)

                page_items.append(folder_items)

        layout[layout_key].append(page_items)


def main():
    # Determine the location of the SQLite Launchpad database
    darwin_user_dir = subprocess.check_output(['getconf', 'DARWIN_USER_DIR']).strip()
    launchpad_db_dir = os.path.join(darwin_user_dir, 'com.apple.dock.launchpad', 'db')
    # print('Using Launchpad database {launchpad_db_path}'.format(
    #     launchpad_db_path=os.path.join(launchpad_db_dir, 'db')
    # ))

    # Connect to the Launchpad SQLite database
    conn = sqlite3.connect(os.path.join(launchpad_db_dir, 'db'))

    # Obtain the root elements for Launchpad apps and Dashboard widgets
    cursor = conn.execute('''
        SELECT key, value
        FROM dbinfo
        WHERE key IN ('launchpad_root', 'dashboard_root');
    ''')

    while True:
        row = cursor.fetchone()
        if row is None:
            break

        key, value = row
        if key == 'launchpad_root':
            launchpad_root = int(value)
        elif key == 'dashboard_root':
            dashboard_root = int(value)

    # Obtain all items and their associated titles
    cursor = conn.execute('''
        SELECT items.rowid, items.parent_id, items.type,
               apps.title AS app_title,
               widgets.title AS widget_title,
               groups.title AS group_title
        FROM items
        LEFT JOIN apps ON apps.item_id = items.rowid
        LEFT JOIN widgets ON widgets.item_id = items.rowid
        LEFT JOIN groups ON groups.item_id = items.rowid
        WHERE items.uuid NOT IN ('ROOTPAGE', 'HOLDINGPAGE',
                                 'ROOTPAGE_DB', 'HOLDINGPAGE_DB',
                                 'ROOTPAGE_VERS', 'HOLDINGPAGE_VERS')
        ORDER BY items.parent_id, items.ordering
    ''')

    # Build a mapping between the parent_id and the associated items
    parent_mapping = defaultdict(list)
    while True:
        row = cursor.fetchone()
        if row is None:
            break

        id, parent_id, type_, app_title, widget_title, group_title = row
        parent_mapping[parent_id].append((id, type_, app_title, widget_title, group_title))

    # Build the current layout
    layout = {
        'app_layout': [],
        'widget_layout': []
    }

    build_layout(launchpad_root, 'app_layout', parent_mapping, layout)
    build_layout(dashboard_root, 'widget_layout', parent_mapping, layout)

    print(yaml.safe_dump(layout, default_flow_style=False, explicit_start=True))


if __name__ == '__main__':
    main()
