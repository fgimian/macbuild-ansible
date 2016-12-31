#!/usr/bin/env python3
import argparse
from collections import defaultdict
import json
import os
import subprocess
import sqlite3
from time import sleep

import yaml


# Colours
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'


class Types(object):
    ROOT = 1
    FOLDER_ROOT = 2
    PAGE = 3
    APP = 4
    DOWNLOADING_APP = 5
    WIDGET = 6


def batch(items, batch_size):
    """
    Batches up a list into multiple lists which each are of the requested batch size;

    :param items: the list of items to be batched
    :param batch_size: the size of each batch
    """
    length = len(items)
    for index in range(0, length, batch_size):
        yield items[index:min(index + batch_size, length)]


def generate_uuid():
    """Generate a UUID using uuidgen."""
    return subprocess.check_output('uuidgen').decode('utf-8').strip()


def get_launchpad_db_dir():
    """Determines the user's Launchpad database directory containing the SQLite database."""
    darwin_user_dir = subprocess.check_output(
        ['getconf', 'DARWIN_USER_DIR']
    ).decode('utf-8').strip()
    return os.path.join(darwin_user_dir, 'com.apple.dock.launchpad', 'db')


def get_mapping(conn, table):
    """
    Obtain a mapping between app ids and their titles.

    :param conn: The SQLite connection.
    :param table: The table to obtain a mapping for (should be apps, widgets or downloading_apps)

    :return: A tuple with two items.  The first value is a dict containing a mapping between
             the title and (id, uuid, flags) for each item.  The second item contains the maximum
             id of the items found.
    """
    cursor = conn.execute(f'''
        SELECT {table}.item_id, {table}.title, items.uuid, items.flags
        FROM {table}
        JOIN items ON items.rowid = {table}.item_id
    ''')

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
    """
    Adds additional pages to the layout containing all items that the user forgot to specify
    in the provided layout.

    :param layout: The layout of items.
    :param mapping: The mapping of the respective items (as obtained by get_mapping).
    """
    items_in_layout = []

    # Iterate through each page of the layout and obtain a list of items contained
    for page in layout:
        # Items on a page
        for item in page:
            # Folders
            if isinstance(item, dict):
                folder_layout = item['folder_layout']

                for folder_page in folder_layout:
                    for title in folder_page:
                        items_in_layout.append(title)

            # Regular items
            else:
                title = item
                items_in_layout.append(title)

    # Determine which items are missing from the layout provided
    missing_items = set(mapping.keys()).difference(items_in_layout)

    # If missing items are found, notify the user and add them to the layout
    if missing_items:
        for missing_items_batch in batch(list(missing_items), 30):
            layout.append(missing_items_batch)

    return missing_items


def setup_items(conn, type_, layout, mapping, group_id, root_parent_id):
    """
    Manipulates the appropriate database table to layout the items as requested by the user.

    :param conn: The SQLite connection.
    :param type_: The type of item being manipulated (usually Types.APP or Types.WIDGET)
    :param layout: The layout requested by the user provided as a list (pages) of lists (items)
                   whereby items are strings.  If the item is a folder, then it is to be a dict
                   with a folder_title and folder_items key and associated values.
    :param mapping: The title to data mapping for the respective items being setup.
    :param group_id: The group id to continue from when adding groups.
    :param root_parent_id: The root parent id to add child items to.

    :return: The resultant group id after additions to continue working from.
    """
    cursor = conn.cursor()

    # Iterate through pages
    for page_ordering, page in enumerate(layout):

        # Start a new page (note that the ordering starts at 1 instead of 0 as there is a
        # holding page at an ordering of 0)
        group_id += 1

        cursor.execute('''
            INSERT INTO items
            (rowid, uuid, flags, type, parent_id, ordering)
            VALUES
            (?, ?, 2, ?, ?, ?)
        ''', (group_id, generate_uuid(), Types.PAGE, root_parent_id, page_ordering + 1)
        )

        cursor.execute('''
            INSERT INTO groups
            (item_id, category_id, title)
            VALUES
            (?, null, null)
        ''', (group_id,)
        )
        conn.commit()

        # Capture the group id of the page to be used for child items
        page_parent_id = group_id

        # Iterate through items
        item_ordering = 0
        for item in page:
            # A folder has been encountered
            if isinstance(item, dict):
                folder_title = item['folder_title']
                folder_layout = item['folder_layout']

                # Start a new folder
                group_id += 1

                cursor.execute('''
                    INSERT INTO items
                    (rowid, uuid, flags, type, parent_id, ordering)
                    VALUES
                    (?, ?, 0, ?, ?, ?)
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

                item_ordering += 1

                # Capture the group id of the folder root to be used for child items
                folder_root_parent_id = group_id

                # Iterate through folder pages
                for folder_page_ordering, folder_page in enumerate(folder_layout):
                    # Start a new folder page
                    group_id += 1

                    cursor.execute('''
                        INSERT INTO items
                        (rowid, uuid, flags, type, parent_id, ordering)
                        VALUES
                        (?, ?, 2, ?, ?, ?)
                    ''', (
                        group_id, generate_uuid(), Types.PAGE, folder_root_parent_id,
                        folder_page_ordering)
                    )

                    cursor.execute('''
                        INSERT INTO groups
                        (item_id, category_id, title)
                        VALUES
                        (?, null, null)
                    ''', (group_id,)
                    )
                    conn.commit()

                    # Iterate through folder items
                    folder_item_ordering = 0
                    for title in folder_page:
                        if title not in mapping:
                            print(f'{RED}Unable to find item {title}, skipping{ENDC}')
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

                        folder_item_ordering += 1

            # Flat items
            else:
                title = item
                if title not in mapping:
                    print(f'{RED}Unable to find item {title}, skipping{ENDC}')
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

                item_ordering += 1

    return group_id


def build_launchpad(config, rebuild_db=True, restart_upon_completion=True):
    """
    Builds the requested layout for both the Launchpad apps and Dashboard widgets by updating
    the user's Launchpad SQlite database.

    :param config: The path containing a YAML or JSON Launchpad configuration.
    :param rebuild_db: Whether or not to re-build the Launchpad database before starting.
    :param restart_upon_completion: Whether or not to restart Launchpad services upon completion.
    """
    widget_layout = config['widget_layout']
    app_layout = config['app_layout']

    # Determine the location of the SQLite Launchpad database
    launchpad_db_dir = get_launchpad_db_dir()
    launchpad_db_path = os.path.join(launchpad_db_dir, 'db')

    print(f'{BLUE}Using Launchpad database {launchpad_db_path}{ENDC}')

    # Re-build the user's database if requested
    if rebuild_db:
        # Delete original Launchpad database and rebuild it for a fresh start
        print(f'{BLUE}Deleting Launchpad database files to perform database rebuild{ENDC}')
        for launchpad_db_file in ['db', 'db-shm', 'db-wal']:
            try:
                os.remove(os.path.join(launchpad_db_dir, launchpad_db_file))
            except OSError:
                pass

        # Restart the Dock to get a freshly built database to work from
        print(f'{BLUE}Restarting the Dock to build a fresh Launchpad databases{ENDC}')
        subprocess.call(['killall', 'Dock'])
        sleep(3)

    # Connect to the Launchpad SQLite database
    conn = sqlite3.connect(launchpad_db_path)

    # Obtain app and widget mappings
    widget_mapping, widget_max_id = get_mapping(conn, 'widgets')
    app_mapping, app_max_id = get_mapping(conn, 'apps')

    # We will begin our group records using the max ids found (groups always appear after
    # apps and widgets)
    group_id = max(app_max_id, widget_max_id)

    # Add any missing widgets from the user's layout to one or more pages after those defined
    missing_widget_items = add_missing_items(widget_layout, widget_mapping)
    if missing_widget_items:
        print(f'{RED}Uncategorised widgets found and added to the last page:{ENDC}')
        for missing_widget_item in missing_widget_items:
            print(f'{RED}- {missing_widget_item}{ENDC}')

    # Add any missing apps from the user's layout to one or more pages after those defined
    missing_app_items = add_missing_items(app_layout, app_mapping)
    if missing_app_items:
        print(f'{RED}Uncategorised apps found and added to the last page:{ENDC}')
        for missing_app_item in missing_app_items:
            print(f'{RED}- {missing_app_item}{ENDC}')

    # Grab a cursor for our operations
    cursor = conn.cursor()

    print(f'{BLUE}Rebuilding the Launchpad database{ENDC}')

    # Clear all items related to groups so we can re-create them
    cursor.execute('''
        DELETE FROM items
        WHERE type IN (?, ?, ?)
    ''', (Types.ROOT, Types.FOLDER_ROOT, Types.PAGE))
    conn.commit()

    # Disable triggers on the items table temporarily so that we may create the rows with our
    # required ordering (including items which have an ordering of 0)
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
        (2, 'HOLDINGPAGE', Types.PAGE, 1),

        # Root for dashboard widgets
        (3, 'ROOTPAGE_DB', Types.ROOT, 0),
        (4, 'HOLDINGPAGE_DB', Types.PAGE, 3),

        # Root for Launchpad version
        (5, 'ROOTPAGE_VERS', Types.ROOT, 0),
        (6, 'HOLDINGPAGE_VERS', Types.PAGE, 5)
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

    # Setup the widgets
    group_id = setup_items(
        conn, Types.WIDGET, widget_layout, widget_mapping, group_id, root_parent_id=3
    )

    # Setup the apps
    group_id = setup_items(conn, Types.APP, app_layout, app_mapping, group_id, root_parent_id=1)

    # Enable triggers on the items again so ordering is auto-generated
    cursor.execute('''
        UPDATE dbinfo
        SET value = 0
        WHERE key = 'ignore_items_update_triggers'
    ''')
    conn.commit()

    if restart_upon_completion:
        # Restart the Dock to that Launchpad can read our new and updated database
        print(f'{BLUE}Restarting the Dock to apply the new database{ENDC}')
        subprocess.call(['killall', 'Dock'])


def build_layout(root, parent_mapping):
    """
    Builds a data structure containing the layout for a particular type of data.

    :param root: The root id of the tree being built.
    :param parent_mapping: The mapping between parent_ids and items.

    :returns: The layout data structure that was built.
    """
    layout = []

    # Iterate through pages
    for page_id, _, _, _, _ in parent_mapping[root]:
        page_items = []

        # Iterate through items
        for id, type_, app_title, widget_title, group_title in parent_mapping[page_id]:
            # An app has been encountered which is added to the page
            if type_ == Types.APP:
                page_items.append(app_title)

            # A widget has been encountered which is added to the page
            elif type_ == Types.WIDGET:
                page_items.append(widget_title)

            # A folder has been encountered
            elif type_ == Types.FOLDER_ROOT:
                # Start a dict for the folder with its title and layout
                folder = {
                    'folder_title': group_title,
                    'folder_layout': []
                }

                # Iterate through folder pages
                for folder_page_id, _, _, _, _ in parent_mapping[id]:
                    folder_page_items = []

                    # Iterate through folder items
                    for (
                        folder_item_id, folder_item_type, folder_item_app_title,
                        folder_widget_title, folder_group_title
                    ) in parent_mapping[folder_page_id]:

                        # An app has been encountered which is being added to the folder page
                        if folder_item_type == Types.APP:
                            folder_page_items.append(folder_item_app_title)

                        # A widget has been encountered which is being added to the folder page
                        elif folder_item_type == Types.WIDGET:
                            folder_page_items.append(folder_widget_title)

                    # Add the page to the folder
                    folder['folder_layout'].append(folder_page_items)

                # Add the folder item to the page
                page_items.append(folder)

        # Add the page to the layout
        layout.append(page_items)

    return layout


def extract_launchpad():
    # Determine the location of the SQLite Launchpad database
    launchpad_db_dir = get_launchpad_db_dir()
    launchpad_db_path = os.path.join(launchpad_db_dir, 'db')

    print(f'{BLUE}Using Launchpad database {launchpad_db_path}{ENDC}')

    # Connect to the Launchpad SQLite database
    conn = sqlite3.connect(launchpad_db_path)

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

    # Build the current layout and return it to the caller
    layout = {
        'app_layout': build_layout(launchpad_root, parent_mapping),
        'widget_layout': build_layout(dashboard_root, parent_mapping),
    }

    return layout


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Create the parser for the build sub-command
    build_parser = subparsers.add_parser(
        'build', help='build the launchpad db using the config provided'
    )
    build_parser.add_argument('config_path', help='the file path of the config to use')

    # Create the parser for the extract sub-command
    extract_parser = subparsers.add_parser(
        'extract', help='extract the launchpad db into a config file'
    )
    extract_parser.add_argument('config_path', help='the file path to extract the config to')
    extract_parser.add_argument(
        '-f', '--format', choices=['json', 'yaml'], default='yaml',
        help='the format to extract your config to'
    )

    # Create the parser for the compare sub-command
    compare_parser = subparsers.add_parser(
        'compare', help='compare the launchpad db with the config'
    )
    compare_parser.add_argument('config_path', help='the file path of the config to compare')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.error('please specify an action to perform')

    print()
    print(f'{BOLD}Launchpad Builder{ENDC}')
    print()

    # Build
    if args.command == 'build':
        with open(args.config_path) as f:
            config = yaml.load(f)

        build_launchpad(config)
        print(
            f'{GREEN}Successfully build the Launchpad layout defined in {args.config_path}{ENDC}'
        )

    # Extract
    elif args.command == 'extract':
        layout = extract_launchpad()
        print(f'{GREEN}Successfully wrote Launchpad config to {args.config_path}{ENDC}')
        with open(args.config_path, 'w') as f:
            if args.format == 'yaml':
                f.write(yaml.safe_dump(layout, default_flow_style=False, explicit_start=True))
            else:
                json.dump(layout, f, indent=2)

    # Compare
    elif args.command == 'compare':
        with open(args.config_path) as f:
            config = yaml.load(f)

        layout = extract_launchpad()

        if config != layout:
            exit(1)

    print()


if __name__ == '__main__':
    main()
