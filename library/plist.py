#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Matthias Neugebauer & Fotis Gimian

DOCUMENTATION = '''
---
module: plist
author: Matthias Neugebauer & Fotis Gimian
short_description: Manage settings in plist files
description:
     - Manage settings in plist files.
options:
  dest:
    description:
      - Domain or absolute path to the plist file; file will be created if
        required. Both regular applications and App Store application plist
        files are searched if a domain is specified.  You may specify
        NSGlobalDomain or "Apple Global Domain" to update global preferences.
    required: true
    default: null
  values:
    description:
      - Values which sould be set or merged represented as a data structure
    type: dict
    required: true
    default: null
  container:
    description:
      - The container name of a sandboxed application (required for App
        Store apps).
    required: false
    default: null
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    required: false
    default: "no"
    choices: [ "yes", "no" ]
notes:
   - All data types are supported by this module (boolean, int, float, string,
     date, array and dict).
   - If a chosen key exists with its own structure, then the plist module
     will merge the value specified with it.
'''

EXAMPLES = '''
plist:
  dest: /tmp/com.ansible.something.plist
  values:
    address: 123 Fake St

plist:
  dest: com.ansible.something
  values:
    count: 7
  backup: yes

plist:
  dest: com.ansible.something
  values:
    person:
      name: Pumpkinhead Man
      occupation: IT Geek
      interests:
        - Python
        - Ansible
        - Pumpkins
'''

import os
import plistlib

def do_plist(module, filename, values, backup=False):
    working_values = values
    changed = False

    try:
        f = open(filename, 'rb')
        plist = plistlib.load(f)
    except IOError:
        plist = {}
    except plistlib.InvalidFileException:
        module.fail_json(msg="an invalid plist already exists")

    changed = not equal(plist, working_values)

    if changed and not module.check_mode:
        if backup:
            module.backup_local(filename)

        try:
            update(plist, working_values)
            plist_dir = os.path.dirname(filename)
            if not os.path.exists(plist_dir):
                os.makedirs(plist_dir)
            f = open(filename, 'wb')
            plistlib.dump(plist, f)
        except Exception as e:
            module.fail_json(msg="Can't change %s" % filename, error=str(e))

    return changed

def equal(slave, master):
    if isinstance(slave, dict) and isinstance(master, dict):
        for key, value in master.items():
            if not equal(slave.get(key), value):
                return False
    else:
        return master == slave

    return True

def update(plist, working_values):
    for key, value in working_values.items():
        if isinstance(value, dict):
            plist[key] = update(plist.get(key, {}), value)
        else:
            plist[key] = working_values[key]

    return plist

def main():
    module = AnsibleModule(
        argument_spec = dict(
            dest = dict(required=True),
            values = dict(required=True, type='dict'),
            container = dict(required=False),
            backup = dict(default='no', type='bool')
        ),
        add_file_common_args = True,
        supports_check_mode = True,
    )

    if (
        not module.params['dest'].startswith('/') and
        not module.params['dest'].startswith('~')
    ):
        if module.params['dest'] in ['NSGlobalDomain', 'Apple Global Domain']:
            module.params['dest'] = os.path.expanduser(
                '~/Library/Preferences/.GlobalPreferences.plist'
            )
        elif module.params['container']:
            module.params['dest'] = os.path.expanduser(
                '~/Library/Containers/%s/Data/Library/Preferences/%s.plist' %
                (module.params['container'], module.params['dest'])
            )
        else:
            module.params['dest'] = os.path.expanduser(
                '~/Library/Preferences/%s.plist' % module.params['dest']
            )
    else:
        module.params['dest'] = os.path.expanduser(module.params['dest'])

    dest = module.params['dest']
    values = module.params['values']
    backup = module.params['backup']

    changed = do_plist(module, dest, values, backup)

    module.exit_json(dest=dest, changed=changed, msg="OK")

# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
