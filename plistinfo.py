#!/usr/bin/env python
from pprint import pprint
import os
from glob import glob
import sys

import biplist


def main():
    try:
        dest = sys.argv[1]
    except IndexError:
        print 'Usage: {} [filename]'.format(__file__)
        exit(1)

    if not dest.startswith('/') and not dest.startswith('~'):
        if dest in ['NSGlobalDomain', 'Apple Global Domain']:
            plist_file = os.path.expanduser(
                '~/Library/Preferences/.GlobalPreferences.plist'
            )
        else:
            plist_file = os.path.expanduser(
                '~/Library/Preferences/%s.plist' % dest
            )
            if not os.path.isfile(plist_file):
                appstore_plist_file = glob(
                    os.path.expanduser(
                        '~/Library/Containers/*/Data/Library/Preferences/%s.plist' %
                        dest
                    )
                )
                if appstore_plist_file:
                    plist_file = appstore_plist_file[0]

        dest = plist_file

    else:

        dest = os.path.expanduser(dest)

    try:
        pprint(biplist.readPlist(dest), indent=2)
    except IOError:
        print 'ERROR: file not found'
        exit(1)


if __name__ == '__main__':
    main()
