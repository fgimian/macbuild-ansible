#!/usr/bin/env python
from __future__ import print_function

import os
from glob import glob
import plistlib
import sys
import yaml

import biplist

# Colours
BOLD = '\033[1m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'


def determine_plist_path(destination):
    # Check for global preferences
    if destination in ['NSGlobalDomain', 'Apple Global Domain']:
        return os.path.expanduser(
            '~/Library/Preferences/.GlobalPreferences.plist'
        )

    # Check for regular user preferences
    user_plist_file = os.path.expanduser(
        '~/Library/Preferences/{bundle_id}.plist'.format(bundle_id=destination)
    )
    if os.path.isfile(user_plist_file):
        return user_plist_file

    # Check for preferences relating to sandboxed apps
    sandboxed_plist_file = glob(
        os.path.expanduser(
            '~/Library/Containers/*/Data'
            '/Library/Preferences/{bundle_id}.plist'.format(bundle_id=destination)
        )
    )
    if sandboxed_plist_file:
        return sandboxed_plist_file[0]

    # If all else fails, assume that the destination is a path reference
    return os.path.expanduser(destination)


def main():
    try:
        destination = sys.argv[1]
    except IndexError:
        print('Usage: {} [filename / bundle_id]'.format(__file__))
        exit(1)
    plist_file = determine_plist_path(destination)

    def plist_data_representer(dumper, data):
        return dumper.represent_str(data)

    def plist_internal_dict_representer(dumper, data):
        return dumper.represent_dict(data)

    yaml.add_representer(biplist.Data, plist_data_representer)
    yaml.add_representer(plistlib._InternalDict, plist_internal_dict_representer)

    try:
        plist_data = biplist.readPlist(plist_file)
        print(yaml.dump(plist_data, default_flow_style=False), end='')
    except IOError:
        print(
            RED +
            'Error: The requested plist file {plist_file} was not '
            'found'.format(plist_file=plist_file) +
            ENDC
        )
        exit(1)
    except biplist.InvalidPlistException:
        print(
            RED +
            'Error: Unable to parse the requested plist '
            'file {plist_file}'.format(plist_file=plist_file) +
            ENDC
        )
        exit(1)


if __name__ == '__main__':
    main()
