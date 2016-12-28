#!/usr/bin/env python3
import os
from glob import glob
import plistlib
import sys
import yaml


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
        return os.path.expanduser('~/Library/Preferences/.GlobalPreferences.plist')

    # Check for regular user preferences
    user_plist_file = os.path.expanduser(f'~/Library/Preferences/{destination}.plist')
    if os.path.isfile(user_plist_file):
        return user_plist_file

    # Check for preferences relating to sandboxed apps
    sandboxed_plist_file = glob(
        os.path.expanduser(f'~/Library/Containers/*/Data/Library/Preferences/{destination}.plist')
    )
    if sandboxed_plist_file:
        return sandboxed_plist_file[0]

    # If all else fails, assume that the destination is a path reference
    return os.path.expanduser(destination)


def main():
    try:
        try:
            plist_file = determine_plist_path(sys.argv[1])
            with open(plist_file, 'rb') as f:
                plist_data = plistlib.load(f)
        except IndexError:
            plist_file = '<stdin>'
            plist_data = plistlib.loads(sys.stdin.buffer.read())

        print(yaml.dump(plist_data, default_flow_style=False), end='')
    except IOError:
        print(f'{RED}Error: The requested plist file {plist_file} was not found{ENDC}')
        exit(1)
    except plistlib.InvalidFileException:
        print(f'{RED}Error: Unable to parse the requested plist file {plist_file}{ENDC}')
        exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
