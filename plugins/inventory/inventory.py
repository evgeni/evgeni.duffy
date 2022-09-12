# Copyright: (c) 2022, Evgeni Golov <evgeni@golov.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: inventory
    short_description: Duffy inventory source
    requirements:
        - duffy
    description:
        - Get inventory hosts from Duffy.
        - Uses a YAML configuration file that ends with ``duffy.(yml|yaml)``.
    options:
      plugin:
        description: token that ensures this is a source file for the C(foreman) plugin.
        required: True
        choices: ['evgeni.duffy.inventory']
      url:
        description:
          - URL of the Duffy API.
          - Taken from the Duffy configuration file if not provided.
      auth_name:
        description:
          - Tenant name.
          - Taken from the Duffy configuration file if not provided.
      auth_key:
        description:
          - API key.
          - Taken from the Duffy configuration file if not provided.
    extends_documentation_fragment:
      - constructed
'''

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.errors import AnsibleError

from ansible_collections.evgeni.duffy.plugins.module_utils.duffy import connect_duffy, HAS_DUFFY


class InventoryModule(BaseInventoryPlugin, Constructable):

    NAME = 'evgeni.duffy.inventory'

    def __init__(self):
        super(InventoryModule, self).__init__()

        if not HAS_DUFFY:
            raise AnsibleError('This script requires duffy[client].')

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('duffy.yaml', 'duffy.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        config = self._read_config_data(path)

        c = connect_duffy(url=self.get_option('url'), auth_name=self.get_option('auth_name'), auth_key=self.get_option('auth_key'))

        sessions = c.list_sessions()
        for session in sessions.sessions:
            for node in session.nodes:
                self.inventory.add_host(node.hostname)

                self.inventory.set_variable(node.hostname, 'ansible_host', str(node.ipaddr))

                host_vars = {'duffy_session': session.id}
                for key, value in dict(node).items():
                    if key in ('hostname', 'ipaddr'):
                        continue
                    host_vars['duffy_{0}'.format(key)] = value
                for key, value in host_vars.items():
                    self.inventory.set_variable(node.hostname, key, value)

                # Determines if composed variables or groups using nonexistent variables is an error
                strict = self.get_option('strict')

                # Add variables created by the user's Jinja2 expressions to the host
                self._set_composite_vars(self.get_option('compose'), host_vars, node.hostname, strict=True)

                # The following two methods combine the provided variables dictionary with the latest host variables
                # Using these methods after _set_composite_vars() allows groups to be created with the composed variables
                self._add_host_to_composed_groups(self.get_option('groups'), host_vars, node.hostname, strict=strict)
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host_vars, node.hostname, strict=strict)
