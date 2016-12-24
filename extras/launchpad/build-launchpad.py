from __future__ import print_function

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
    return subprocess.check_output('uuidgen').strip()


def get_mapping(conn, table):
    """
    Obtain a mapping between app ids and their titles.

    :param conn: The SQLite connection.
    :param table: The table to obtain a mapping for (should be apps, widgets or downloading_apps)

    :return: A tuple with two items.  The first value is a dict containing a mapping between
             the title and (id, uuid, flags) for each item.  The second item contains the maximum
             id of the items found.
    """
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
            (?, ?, 0, ?, ?, ?)
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
                        (?, ?, 0, ?, ?, ?)
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

                        folder_item_ordering += 1

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

                item_ordering += 1

    return group_id


def main():
    # Load the user's layout
    with open('launchpad-layout.yaml') as f:
        config = yaml.load(f)

    widget_layout = config['widget_layout']
    app_layout = config['app_layout']

    # Determine the location of the SQLite Launchpad database
    darwin_user_dir = subprocess.check_output(['getconf', 'DARWIN_USER_DIR']).strip()
    launchpad_db_dir = os.path.join(darwin_user_dir, 'com.apple.dock.launchpad', 'db')
    print('Using Launchpad database {launchpad_db_path}'.format(
        launchpad_db_path=os.path.join(launchpad_db_dir, 'db')
    ))

    # Delete original Launchpad database and rebuild it for a fresh start
    print('Deleting Launchpad database files')
    for launchpad_db_file in ['db', 'db-shm', 'db-wal']:
        try:
            os.remove(os.path.join(launchpad_db_dir, launchpad_db_file))
        except OSError:
            pass

    # Restart the Dock to get a freshly built database to work from
    print('Restarting the Dock to build a fresh Launchpad databases')
    subprocess.call(['killall', 'Dock'])
    sleep(3)

    # Connect to the Launchpad SQLite database
    conn = sqlite3.connect(os.path.join(launchpad_db_dir, 'db'))

    # Obtain app and widget mappings
    widget_mapping, widget_max_id = get_mapping(conn, 'widgets')
    app_mapping, app_max_id = get_mapping(conn, 'apps')

    # We will begin our group records using the max ids found (groups always appear after
    # apps and widgets)
    group_id = max(app_max_id, widget_max_id)

    # Add any missing widgets from the user's layout to one or more pages after those defined
    missing_widget_items = add_missing_items(widget_layout, widget_mapping)
    if missing_widget_items:
        print('Uncategorised items found and added to the last page: ' + str(missing_widget_items))

    # Add any missing apps from the user's layout to one or more pages after those defined
    missing_app_items = add_missing_items(app_layout, app_mapping)
    if missing_app_items:
        print('Uncategorised items found and added to the last page: ' + str(missing_app_items))

    # Grab a cursor for our operations
    cursor = conn.cursor()

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
        conn, Types.WIDGET, widget_layout, widget_mapping, group_id,
        root_parent_id=3
    )

    # Setup the apps
    group_id = setup_items(
        conn, Types.APP, app_layout, app_mapping, group_id,
        root_parent_id=1
    )

    # Enable triggers on the items again so ordering is auto-generated
    cursor.execute('''
        UPDATE dbinfo
        SET value = 0
        WHERE key = 'ignore_items_update_triggers'
    ''')
    conn.commit()

    # Restart the Dock to that Launchpad can read our new and updated database
    print('Restarting the Dock to see the updates we made')
    subprocess.call(['killall', 'Dock'])


if __name__ == '__main__':
    main()
