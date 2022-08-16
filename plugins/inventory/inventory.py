import duffy.client
from duffy.cli import DEFAULT_CONFIG_PATHS
from duffy.configuration import config, read_configuration

# [SessionNodeModel(
#    hostname='n27-12-108.pool.ci.centos.org',
#    ipaddr=IPv4Address('172.27.12.108'),
#    comment=None,
#    pool='virt-ec2-t2-centos-8s-x86_64',
#    reusable=False,
#    data={
#      'provision': {'ec2_instance_id': 'i-0de7532e64cf0b453', 'ec2_instance_type': 't2.2xlarge', 'hostname': 'n27-12-108.pool.ci.centos.org', 'ipaddr': '172.27.12.108', 'public_hostname': 'ec2-54-144-181-107.compute-1.amazonaws.com', 'public_ipaddress': '54.144.181.107'},
#      'nodes_spec': {'quantity': 1, 'pool': 'virt-ec2-t2-centos-8s-x86_64'}},
#    id=1036,
#    state='deployed'
# )]

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

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

        c = duffy.client.DuffyClient()

        sessions = c.list_sessions()
        for session in sessions.sessions:
            for node in session.nodes:
                self.inventory.add_host(node.hostname)
                self.inventory.set_variable(node.hostname, 'ansible_host', str(node.ipaddr))
