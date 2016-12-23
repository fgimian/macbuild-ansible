from __future__ import print_function

import os
import subprocess
import sqlite3
from time import sleep
import yaml


class Types(object):
    ROOT = 1
    FOLDER_ROOT = 2
    GROUP = 3
    APP = 4
    DOWNLOADING_APP = 5
    WIDGET = 6


def generate_uuid():
    return subprocess.check_output('uuidgen').strip()


def get_mapping(conn, table):
    # Obtain a mapping between app ids and their titles
    cursor = conn.execute('''
        SELECT {table}.item_id, {table}.title, items.uuid, items.flags
        FROM {table}
        JOIN items ON items.rowid = {table}.item_id
    '''.format(table=table))

    mapping = {}
    max_id = 0

    while True:
        # Grab the current row
        row = cursor.fetchone()
        if row is None:
            break

        # Unpack the row and add it to our mapping
        id, title, uuid, flags = row
        mapping[title] = (id, uuid, flags)

        # Obtain the maximum id in this table
        max_id = max(max_id, id)

    return mapping, max_id


def add_missing_items(layout, mapping):
    items_in_layout = []
    for page in layout:
        for item in page:
            if isinstance(item, dict):
                folder_layout = item.values()[0]
                for folder_page in folder_layout:
                    for title in folder_page:
                        items_in_layout.append(title)
            else:
                title = item
                items_in_layout.append(title)

    missing_items = set(mapping.keys()).difference(items_in_layout)

    if missing_items:
        print('Uncategorised items found and added to the last page: ' + str(missing_items))
        layout.append(list(missing_items))


def setup_items(conn, type_, layout, mapping, group_id, root_parent_id):
    cursor = conn.cursor()

    for page_ordering, page in enumerate(layout):

        # Start a new page
        group_id += 1

        cursor.execute('''
            INSERT INTO items
            (rowid, uuid, flags, type, parent_id, ordering)
            VALUES
            (?, ?, 0, ?, ?, ?)
        ''', (group_id, generate_uuid(), Types.GROUP, root_parent_id, page_ordering + 1)
        )

        cursor.execute('''
            INSERT INTO groups
            (item_id, category_id, title)
            VALUES
            (?, null, null)
        ''', (group_id,)
        )
        conn.commit()

        page_parent_id = group_id

        # Go through items for the current page
        for item_ordering, item in enumerate(page):
            # A folder has been encountered
            if isinstance(item, dict):
                folder_title, folder_layout = item.items()[0]

                # Start a new folder (requires two groups)
                group_id += 1

                cursor.execute('''
                    INSERT INTO items
                    (rowid, uuid, flags, type, parent_id, ordering)
                    VALUES
                    (?, ?, 1, ?, ?, ?)
                ''', (group_id, generate_uuid(), Types.FOLDER_ROOT, page_parent_id, item_ordering)
                )

                cursor.execute('''
                    INSERT INTO groups
                    (item_id, category_id, title)
                    VALUES
                    (?, null, ?)
                    ''', (group_id, folder_title)
                )
                conn.commit()

                folder_parent_id = group_id

                for folder_page_ordering, folder_page in enumerate(folder_layout):

                    group_id += 1

                    cursor.execute('''
                        INSERT INTO items
                        (rowid, uuid, flags, type, parent_id, ordering)
                        VALUES
                        (?, ?, 0, ?, ?, ?)
                    ''', (group_id, generate_uuid(), Types.GROUP, folder_parent_id, folder_page_ordering)
                    )

                    cursor.execute('''
                        INSERT INTO groups
                        (item_id, category_id, title)
                        VALUES
                        (?, null, null)
                    ''', (group_id,)
                    )
                    conn.commit()

                    for folder_item_ordering, title in enumerate(folder_page):
                        if title not in mapping:
                            print('Unable to find item {title}, skipping'.format(title=title))
                            continue

                        item_id, uuid, flags = mapping[title]
                        cursor.execute('''
                            UPDATE items
                            SET uuid = ?,
                                flags = ?,
                                type = ?,
                                parent_id = ?,
                                ordering = ?
                            WHERE rowid = ?
                        ''', (
                                uuid,
                                flags,
                                type_,
                                group_id,
                                folder_item_ordering,
                                item_id
                            )
                        )
                        conn.commit()

            # Flat items
            else:
                title = item
                if title not in mapping:
                    print('Unable to find item {title}, skipping'.format(title=title))
                    continue

                item_id, uuid, flags = mapping[title]
                cursor.execute('''
                    UPDATE items
                    SET uuid = ?,
                        flags = ?,
                        type = ?,
                        parent_id = ?,
                        ordering = ?
                    WHERE rowid = ?
                ''', (
                        uuid,
                        flags,
                        type_,
                        page_parent_id,
                        item_ordering,
                        item_id
                    )
                )
                conn.commit()

    return group_id


def main():
    # Load user config
    with open('launchpad-layout.yaml') as f:
        config = yaml.load(f)

    app_layout = config['app_layout']
    widget_layout = config['widget_layout']

    # Determine the location of the SQLite Launchpad database
    darwin_user_dir = subprocess.check_output(
        ['getconf', 'DARWIN_USER_DIR']
    ).strip()

    launchpad_db_dir = os.path.join(
        darwin_user_dir, 'com.apple.dock.launchpad', 'db'
    )

    print('Using Launchpad database {launchpad_db_path}'.format(
        launchpad_db_path=os.path.join(launchpad_db_dir, 'db')
    ))

    # Delete original Launchpad database and rebuild it for a fresh start
    print('Deleting Launchpad database files')
    try:
        os.remove(os.path.join(launchpad_db_dir, 'db'))
        os.remove(os.path.join(launchpad_db_dir, 'db-shm'))
        os.remove(os.path.join(launchpad_db_dir, 'db-wal'))
    except OSError:
        pass
    print('Restarting the Dock to build a fresh Launchpad databases')
    subprocess.call(['killall', 'Dock'])
    sleep(3)

    # Connect to the Launchpad SQLite database
    conn = sqlite3.connect(os.path.join(launchpad_db_dir, 'db'))

    # Obtain app and widget mappings
    app_mapping, app_max_id = get_mapping(conn, 'apps')
    widget_mapping, widget_max_id = get_mapping(conn, 'widgets')

    # We will begin our group records using the max ids found ready for
    # increment later on
    group_id = max(app_max_id, widget_max_id)

    # Grab a cursor for our operations
    cursor = conn.cursor()

    # Add any missing items to the last page
    add_missing_items(app_layout, app_mapping)
    add_missing_items(widget_layout, widget_mapping)

    # Clear all items related to groups so we can re-create them
    cursor.execute('''
        DELETE FROM items
        WHERE type IN (?, ?, ?)
    ''', (Types.ROOT, Types.FOLDER_ROOT, Types.GROUP))
    conn.commit()

    # Disable triggers on the items table temporarily so that we may
    # create the root rows with ordering of 0
    cursor.execute('''
        UPDATE dbinfo
        SET value = 1
        WHERE key = 'ignore_items_update_triggers'
    ''')
    conn.commit()

    # Add root and holding pages to items and groups
    for rowid, uuid, type_, parent_id in [
        # Root for Launchpad apps
        (1, 'ROOTPAGE', Types.ROOT, 0),
        (2, 'HOLDINGPAGE', Types.GROUP, 1),

        # Root for dashboard widgets
        (3, 'ROOTPAGE_DB', Types.ROOT, 0),
        (4, 'HOLDINGPAGE_DB', Types.GROUP, 3),

        # Root for Launchpad version
        (5, 'ROOTPAGE_VERS', Types.ROOT, 0),
        (6, 'HOLDINGPAGE_VERS', Types.GROUP, 5)
    ]:
        cursor.execute('''
            INSERT INTO items
            (rowid, uuid, flags, type, parent_id, ordering)
            VALUES (?, ?, null, ?, ?, 0)
        ''', (rowid, uuid, type_, parent_id))

        cursor.execute('''
            INSERT INTO groups
            (item_id, category_id, title)
            VALUES
            (?, null, null)
        ''', (rowid,))

    conn.commit()

    # Setup the apps
    group_id = setup_items(
        conn, Types.APP, app_layout, app_mapping, group_id,
        root_parent_id=1
    )

    # Setup the widgets
    group_id = setup_items(
        conn, Types.WIDGET, widget_layout, widget_mapping, group_id,
        root_parent_id=3
    )

    # Enable triggers on the items again so ordering is auto-generated
    cursor.execute('''
        UPDATE dbinfo
        SET value = 0
        WHERE key = 'ignore_items_update_triggers'
    ''')
    conn.commit()

    print('Restarting the Dock to see the updates we made')
    subprocess.call(['killall', 'Dock'])


if __name__ == '__main__':
    main()
