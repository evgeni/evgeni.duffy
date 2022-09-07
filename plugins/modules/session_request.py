#!/usr/bin/python

# Copyright: (c) 2022, Evgeni Golov <evgeni@golov.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: session_request
author:
    - Evgeni Golov (@evgeni)
short_description: Request a Duffy session
version_added: "1.0.0"
description: Request a Duffy session
options:
    pool:
        description: The pool to request the session from.
        required: true
        type: str
    quantity:
        description: The number of nodes to be requested.
        required: false
        type: int
        default: 1
extends_documentation_fragment:
  - evgeni.duffy.duffy
'''

EXAMPLES = r'''
- name: Request session from pool virt-ec2-t2-centos-8s-x86_64
  evgeni.duffy.session_request:
    pool: virt-ec2-t2-centos-8s-x86_64
    quantity: 1
'''

RETURN = r'''
session:
    description: The ID of the session that was requested.
    type: int
    returned: success
    sample: 1
'''


import json
from ansible_collections.evgeni.duffy.plugins.module_utils.duffy import DuffyAnsibleModule, DuffyAPIErrorModel


def _json_dumpable_dict(a_dict):
    result = {}

    for (k, v) in a_dict.items():
        try:
            json.dumps(v)
        except TypeError:
            v = str(v)
        result[k] = v

    return result


class DuffySessionRequestAnsibleModule(DuffyAnsibleModule):

    def run(self):
        if not self.check_mode:
            result = self.client.request_session([{'pool': self.params.get('pool'), 'quantity': self.params.get('quantity')}])
            if isinstance(result, DuffyAPIErrorModel):
                self.fail_json(msg=str(result))

            session = result.session.id
            nodes = [_json_dumpable_dict(dict(node)) for node in result.session.nodes]
        else:
            session = 0
            nodes = []

        self.exit_json(session=session, changed=True, nodes=nodes)


def main():
    module = DuffySessionRequestAnsibleModule(
        argument_spec=dict(
            pool=dict(required=True),
            quantity=dict(required=False, type='int', default=1)
        ),
    )

    with module.api_client():
        module.run()


if __name__ == '__main__':
    main()
