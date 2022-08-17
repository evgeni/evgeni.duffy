#!/usr/bin/python

# Copyright: (c) 2022, Evgeni Golov <evgeni@golov.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: session_retire
author:
    - Evgeni Golov (@evgeni)
short_description: Retire a Duffy session
version_added: "1.0.0"
description: Retire a Duffy session
options:
    session_id:
        description: The ID of the session to retire.
        required: true
        type: int
'''

EXAMPLES = r'''
- name: Retire session 1
  evgeni.duffy.session_retire:
    session_id: 1
'''

RETURN = r'''
session:
    description: The ID of the session that was retired.
    type: int
    returned: success
    sample: 1
'''


from ansible_collections.evgeni.duffy.plugins.module_utils.duffy import DuffyAnsibleModule
from duffy.client.main import DuffyAPIErrorModel


class DuffySessionRetireAnsibleModule(DuffyAnsibleModule):

    def run(self):
        changed = False
        session = self.params.get('session_id')
        result = self.client.show_session(session)

        if isinstance(result, DuffyAPIErrorModel):
            session = None
        else:
            if result.session.retired_at is None:
                if not self.check_mode:
                    self.client.retire_session(session)
                changed = True

        self.exit_json(session=session, changed=changed)


def main():
    module = DuffySessionRetireAnsibleModule(
        argument_spec=dict(
            session_id=dict(required=True, type='int')
        ),
    )

    with module.api_client():
        module.run()

if __name__ == '__main__':
    main()
