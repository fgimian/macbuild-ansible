#!/usr/bin/python
#
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
  key:
    description:
      - Key in the plist to manage.
    required: false
    default: null
  value:
    description:
     - Value which sould be set or merged (may be a complex data type like a
       dict or array).
    required: true
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
   - If any a chosen key exists with its own structure, then the plist module
     will merge the value specified with it.
requirements: [ biplist ]
'''

EXAMPLES = '''
plist:
  dest: /tmp/com.ansible.something.plist
  key: address
  value: 123 Fake St

plist:
  dest: com.ansible.something
  key: count
  value: 7
  backup: yes

plist:
  dest: com.ansible.something
  key: person
  value:
    name: Pumpkinhead Man
    occupation: IT Geek
    interests:
      - Python
      - Ansible
      - Pumpkins
'''

from glob import glob
import os

try:
    import biplist
except ImportError:
    biplist_found = False
else:
    biplist_found = True

def do_plist(module, filename, key, value, backup=False):
    changed = False

    try:
        f = open(filename)
        plist = biplist.readPlist(f)
    except IOError:
        plist = {}
    except biplist.InvalidPlistException:
        module.fail_json(msg="an invalid plist already exists")

    working_value = {key: value}
    changed = not equal(plist, working_value)

    if changed and not module.check_mode:
        if backup:
            module.backup_local(filename)

        try:
            update(plist, working_value)
            f = open(filename, 'w')
            biplist.writePlist(plist, f)
        except Exception as e:
            module.fail_json(msg="Can't change %s" % filename, error=str(e))

    return changed

def equal(slave, master):
    if isinstance(slave, dict) and isinstance(master, dict):
        for key, value in master.iteritems():
            if not equal(slave.get(key), value):
                return False
    else:
        return master == slave

    return True

def update(plist, working_value):
    for key, value in working_value.iteritems():
        if isinstance(value, dict):
            plist[key] = update(plist.get(key, {}), value)
        else:
            plist[key] = working_value[key]

    return plist

def main():
    module = AnsibleModule(
        argument_spec = dict(
            dest = dict(required=True),
            key = dict(required=True),
            value = dict(required=True),
            backup = dict(default='no', type='bool')
        ),
        add_file_common_args = True,
        supports_check_mode = True,
    )

    if not biplist_found:
        module.fail_json(msg="the python biplist module is required")

    if not module.params['dest'].startswith('/'):
        if module.params['dest'] in ['NSGlobalDomain', 'Apple Global Domain']:
            plist_file = os.path.expanduser(
                '~/Library/Preferences/.GlobalPreferences.plist'
            )
        else:
            plist_file = os.path.expanduser(
                '~/Library/Preferences/%s.plist' % module.params['dest']
            )
            if not os.path.isfile(plist_file):
                appstore_plist_file = glob(
                    os.path.expanduser(
                        '~/Library/Containers/*/Data/Library/Preferences/%s.plist' %
                        module.params['dest']
                    )
                )
                if appstore_plist_file:
                    plist_file = appstore_plist_file[0]

        module.params['dest'] = plist_file

    dest = module.params['dest']
    key = module.params['key']
    value = module.params['value']
    backup = module.params['backup']

    changed = do_plist(module, dest, key, value, backup)

    module.exit_json(dest=dest, changed=changed, msg="OK")

# import module snippets
from ansible.module_utils.basic import *
main()
