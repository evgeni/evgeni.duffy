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
'''

from ansible.plugins.inventory import BaseInventoryPlugin

from duffy.cli import DEFAULT_CONFIG_PATHS
from duffy.client import DuffyClient
from duffy.configuration import config, read_configuration


class InventoryModule(BaseInventoryPlugin):

    NAME = 'evgeni.duffy.inventory'

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

        config_paths = tuple(path for path in DEFAULT_CONFIG_PATHS if path.exists())
        read_configuration(*config_paths, clear=True, validate=True)

        c = DuffyClient(url=self.get_option('url'), auth_name=self.get_option('auth_name'), auth_key=self.get_option('auth_key'))

        sessions = c.list_sessions()
        for session in sessions.sessions:
            for node in session.nodes:
                self.inventory.add_host(node.hostname)
                self.inventory.set_variable(node.hostname, 'ansible_host', str(node.ipaddr))
                for key, value in dict(node).items():
                    if key in ('hostname', 'ipaddr'):
                        continue
                    self.inventory.set_variable(node.hostname, 'duffy_{}'.format(key), value)
