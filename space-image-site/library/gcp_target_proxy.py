#!/usr/bin/python
# TODO(supertom): gce_net_targetproxy IN PROGRESS
# Copyright 2016 Google Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}
DOCUMENTATION = '''
'''

EXAMPLES = '''
'''

RETURN = '''
'''


try:
    import libcloud
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver
    from libcloud.common.google import GoogleBaseError, QuotaExceededError, \
        ResourceExistsError, ResourceInUseError, ResourceNotFoundError
    from libcloud.compute.drivers.gce import GCEAddress
    _ = Provider.GCE
    HAS_LIBCLOUD = True
except ImportError:
    HAS_LIBCLOUD = False

try:
    from ast import literal_eval
    HAS_PYTHON26 = True
except ImportError:
    HAS_PYTHON26 = False

def get_targethttpproxy(gce, name):
    """
    Get a Targethttpproxy from GCE.

    :param gce: An initialized GCE driver object.
    :type gce:  :class: `GCENodeDriver`

    :param name: Name of the Target Proxy.
    :type name:  ``str``

    :return: A GCETargethttpproxy object or None.
    :rtype: :class: `GCETargethttpproxy` or None
    """
    try:
        # Does the Target Proxy already exist?
        return gce.ex_get_targethttpproxy(name=name)

    except ResourceNotFoundError:
        return None

def get_healthcheck(gce, name):
    return gce.ex_get_healthcheck(name)

def get_instancegroup(gce, name, zone):
    return gce.ex_get_instancegroup(name=name, zone=zone)
    
def create_targethttpproxy(gce, params):
    """
    Create a new Target Proxy.

    :param gce: An initialized GCE driver object.
    :type gce:  :class: `GCENodeDriver`

    :param params: Dictionary of parameters needed by the module.
    :type params:  ``dict``

    :return: Tuple with changed stats and TODO(supertom): something here.
    :rtype: tuple in the format of (bool, list)
    """
    changed = False
    return_data = []

    urlmap = gce.ex_get_urlmap(name=params['urlmap'])
    targethttpproxy = gce.ex_create_targethttpproxy(
        name=params['name'], urlmap=urlmap)

    if targethttpproxy:
        changed = True
        return_data = { 'name': params['name'], 'urlmap': urlmap.name }

    return (changed, return_data)

def delete_targethttpproxy(targethttpproxy):
    """
    Delete a Targethttpproxy.
    """
    changed = False
    return_data = []
    if targethttpproxy.destroy():
        changed = True
        return_data = True
    return (changed, return_data)

def main():
    module = AnsibleModule(argument_spec=dict(
        name=dict(required=True),
        state=dict(choices=['absent', 'present'], default='present'),
        urlmap=dict(required=True),
        service_account_email=dict(),
        service_account_permissions=dict(type='list'),
        pem_file=dict(),
        credentials_file=dict(),
        project_id=dict(), ), )

    if not HAS_PYTHON26:
        module.fail_json(
            msg="GCE module requires python's 'ast' module, python v2.6+")
    # if not HAS_LIBCLOUD:
    #     module.fail_json(
    #         msg='libcloud with GCE Managed Instance Group support (1.2+) required for this module.')

    gce = gce_connect(module)
    # if not hasattr(gce, 'ex_create_instancegroupmanager'):
    #     module.fail_json(
    #         msg='libcloud with GCE Managed Instance Group support (1.2+) required for this module.',
    #         changed=False)

    params = {}
    params['state'] = module.params.get('state')
    params['name'] = module.params.get('name')
    params['urlmap'] = module.params.get('urlmap')

    changed = False
    json_output = {'state': params['state']}
    targethttpproxy = get_targethttpproxy(gce, params['name'])

    if not targethttpproxy:
        if params['state'] == 'absent':
            # Doesn't exist in GCE, and state==absent.
            changed = False
            module.fail_json(
                msg="Cannot delete unknown targethttpproxy: %s" %
                (params['name']))
        else:
            # Create
            (changed, json_output['targethttpproxy']) = create_targethttpproxy(gce,
                                                             params)
    elif params['state'] == 'absent':
        # Delete
        (changed, json_output['targethttpproxy']) = delete_targethttpproxy(targethttpproxy)
    else:
        # Update
        pass

    json_output['changed'] = changed
    json_output.update(params)
    module.exit_json(**json_output)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.gce import *
if __name__ == '__main__':
    main()
