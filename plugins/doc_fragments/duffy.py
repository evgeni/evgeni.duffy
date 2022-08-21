from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = '''
requirements:
  - requests
options:
  url:
    description:
      - URL of the Duffy API.
      - Taken from the Duffy configuration file if not provided.
    type: str
    required: false
  auth_name:
    description:
      - Tenant name.
      - Taken from the Duffy configuration file if not provided.
    type: str
    required: false
  auth_key:
    description:
      - API key.
      - Taken from the Duffy configuration file if not provided.
    type: str
    required: false
    '''
