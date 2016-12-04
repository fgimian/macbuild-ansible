from __future__ import print_function

import os
from pprint import pprint
import random
import subprocess
import sqlite3
import string
from time import sleep

widget_layout = [
    [
        "Calendar",
        "Calculator",
        "Contacts",
        "Dictionary",
        "ESPN",
        "Flight Tracker",
        "Movies",
        "Ski Report",
        "Stickies",
        "Stocks",
        "Tile Game",
        "Translation",
        "Unit Converter",
        "Weather",
        "Web Clip",
        "World Clock",
    ]
]
app_layout = [
    [
        "App Store",
        "Automator",
        "Calculator",
        "Calendar",
        "Chess",
        "Clear",
        "Contacts",
        "Dashboard",
        "Dictionary",
        "DVD Player",
        "FaceTime",
        "Flux",
        "Focusrite Control",
        "Font Book",
        "Google Chrome",
        "iBooks",
        "Image Capture",
        "Install OS X El Capitan",
        "iTunes",
        "MacDown",
        "Mail",
        "Maps",
        "Messages",
        "Mission Control",
        "Notes",
        "Photo Booth",
        "Photos",
        "QuickTime Player",
        "Preview",
    ],
    [
        "Reminders",
        "Safari",
        "Siri",
        "Stickies",
        "Sublime Text",
        "System Preferences",
        "TextEdit",
        "Time Machine",
        "Activity Monitor",
        "AirPort Utility",
        "Audio MIDI Setup",
        "Bluetooth File Exchange",
        "Boot Camp Assistant",
        "ColorSync Utility",
        "Console",
        "Digital Color Meter",
        "Disk Utility",
        "Grab",
        "Grapher",
        "Keychain Access",
        "Migration Assistant",
        "Script Editor",
        "System Information",
        "Terminal",
        "VoiceOver Utility",
    ],
]


class Types(object):
    ROOT = 1
    FOLDER = 2
    GROUP = 3
    APP = 4
    WIDGET = 6


def generate_uuid():
    r = ''.join(
        random.choice(string.digits + string.ascii_uppercase[:6])
        for _ in range(32)
    )
    return '-'.join([r[:8], r[8:12], r[12:16], r[16:20], r[20:]])



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


def setup_items(cursor, type_, layout, mapping, group_id, group_parent_id):
    for page in layout:

        # Start a new page
        group_id += 1

        cursor.execute('''
            INSERT INTO items
            (rowid, uuid, flags, type, parent_id)
            VALUES
            (?, ?, 0, ?, ?)
        ''', (group_id, generate_uuid(), Types.GROUP, group_parent_id)
        )

        cursor.execute('''
            INSERT INTO groups
            (item_id, category_id, title)
            VALUES
            (?, null, null)
        ''', (group_id,)
        )

        # Go through items for the current page
        for title in page:
            print(title)
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

    return group_id


def main():
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
        cursor, Types.WIDGET, widget_layout, widget_mapping, group_id,
        group_parent_id=3
    )
    conn.commit()

    # Setup the apps
    group_id = setup_items(
        cursor, Types.APP, app_layout, app_mapping, group_id,
        group_parent_id=1
    )
    conn.commit()

    print('Restarting the Dock to see the updates we made')
    subprocess.call(['killall', 'Dock'])

if __name__ == '__main__':
    main()
