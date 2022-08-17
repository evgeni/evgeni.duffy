# Copyright: (c) 2022, Evgeni Golov <evgeni@golov.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from contextlib import contextmanager

from ansible.module_utils.basic import AnsibleModule

from duffy.cli import DEFAULT_CONFIG_PATHS
from duffy.client import DuffyClient
from duffy.configuration import config, read_configuration


class DuffyAnsibleModule(AnsibleModule):

    def __init__(self, **kwargs):
        argument_spec = dict(
            url=dict(required=False),
            auth_name=dict(required=False),
            auth_key=dict(required=False, no_log=True),
        )
        argument_spec.update(kwargs.pop('argument_spec', {}))
        supports_check_mode = kwargs.pop('supports_check_mode', True)

        super(DuffyAnsibleModule, self).__init__(argument_spec=argument_spec, supports_check_mode=supports_check_mode, **kwargs)


    @contextmanager
    def api_client(self):
        config_paths = tuple(path for path in DEFAULT_CONFIG_PATHS if path.exists())
        read_configuration(*config_paths, clear=True, validate=True)

        self.client = DuffyClient(url=self.params.get('url'), auth_name=self.params.get('auth_name'), auth_key=self.params.get('auth_key'))

        yield

        self.exit_json()