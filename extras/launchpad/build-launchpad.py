from __future__ import print_function

import os
import random
import subprocess
import sqlite3
import string
from time import sleep
import yaml


class Types(object):
    ROOT = 1
    FOLDER = 2
    GROUP = 3
    APP = 4
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


def setup_items(conn, type_, layout, mapping, group_id, root_parent_id):
    cursor = conn.cursor()

    for page in layout:

        # Start a new page
        group_id += 1

        cursor.execute('''
            INSERT INTO items
            (rowid, uuid, flags, type, parent_id)
            VALUES
            (?, ?, 0, ?, ?)
        ''', (group_id, generate_uuid(), Types.GROUP, root_parent_id)
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
        for item in page:
            # A folder has been encountered
            if isinstance(item, dict):
                folder_title, folder_items = item.items()[0]

                # Start a new folder (requires two groups)
                group_id += 1

                cursor.execute('''
                    INSERT INTO items
                    (rowid, uuid, flags, type, parent_id)
                    VALUES
                    (?, ?, 1, ?, ?)
                ''', (group_id, generate_uuid(), Types.FOLDER, page_parent_id)
                )

                cursor.execute('''
                    INSERT INTO groups
                    (item_id, category_id, title)
                    VALUES
                    (?, null, ?)
                ''', (group_id, folder_title)
                )

                folder_parent_id = group_id

                group_id += 1

                cursor.execute('''
                    UPDATE dbinfo
                    SET value = 1
                    WHERE key = 'ignore_items_update_triggers'
                ''')
                conn.commit()

                cursor.execute('''
                    INSERT INTO items
                    (rowid, uuid, flags, type, parent_id, ordering)
                    VALUES
                    (?, ?, 0, ?, ?, 0)
                ''', (group_id, generate_uuid(), Types.GROUP, folder_parent_id)
                )

                cursor.execute('''
                    INSERT INTO groups
                    (item_id, category_id, title)
                    VALUES
                    (?, null, null)
                ''', (group_id,)
                )
                conn.commit()

                cursor.execute('''
                    UPDATE dbinfo
                    SET value = 0
                    WHERE key = 'ignore_items_update_triggers'
                ''')
                conn.commit()

                for title in folder_items:
                    item_id, uuid, flags = mapping[title]
                    cursor.execute('''
                        UPDATE items
                        SET uuid = ?,
                            flags = ?,
                            type = ?,
                            parent_id = ?
                        WHERE rowid = ?
                    ''', (uuid, flags, type_, group_id, item_id)
                    )

            # Flat items
            else:
                title = item
                item_id, uuid, flags = mapping[title]
                cursor.execute('''
                    UPDATE items
                    SET uuid = ?,
                        flags = ?,
                        type = ?,
                        parent_id = ?
                    WHERE rowid = ?
                ''', (uuid, flags, type_, page_parent_id, item_id)
                )

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
        'private', darwin_user_dir, 'com.apple.dock.launchpad', 'db'
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
    sleep(1)

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

    # Clear the items and groups tables
    cursor.execute('''
        DELETE FROM items
        WHERE type IN (?, ?, ?)
    ''', (Types.ROOT, Types.FOLDER, Types.GROUP))
    cursor.execute('DELETE FROM groups')
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

    # Enable triggers on the items again so ordering is auto-generated
    cursor.execute('''
        UPDATE dbinfo
        SET value = 0
        WHERE key = 'ignore_items_update_triggers'
    ''')
    conn.commit()

    # Setup the widgets
    group_id = setup_items(
        conn, Types.WIDGET, widget_layout, widget_mapping, group_id,
        root_parent_id=3
    )
    conn.commit()

    # Setup the apps
    group_id = setup_items(
        conn, Types.APP, app_layout, app_mapping, group_id,
        root_parent_id=1
    )
    conn.commit()

    print('Restarting the Dock to see the updates we made')
    subprocess.call(['killall', 'Dock'])


if __name__ == '__main__':
    main()
