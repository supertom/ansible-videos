#!/usr/bin/python
# TODO(supertom): gce_forwardingrule IN PROGRESS
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
    from libcloud.compute.drivers.gce import GCEForwardingrule
    _ = Provider.GCE
    HAS_LIBCLOUD = True
except ImportError:
    HAS_LIBCLOUD = False

try:
    from ast import literal_eval
    HAS_PYTHON26 = True
except ImportError:
    HAS_PYTHON26 = False

def get_address(gce, name, region='global'):
    """
    Get a Address from GCE.

    :param gce: An initialized GCE driver object.
    :type gce:  :class: `GCENodeDriver`

    :param name: Name of the Target Proxy.
    :type name:  ``str``

    :return: A GCEAddress object or None.
    :rtype: :class: `GCEAddress` or None
    """
    try:
        # Does the Target Proxy already exist?
        return gce.ex_get_address(name=name, region=region)

    except ResourceNotFoundError:
        return None
def get_forwardingrule(gce, name, region=None, global_rule=True):
    """
    Get a Forwardingrule from GCE.

    :param gce: An initialized GCE driver object.
    :type gce:  :class: `GCENodeDriver`

    :param name: Name of the Forwardingrule.
    :type name:  ``str``

    :return: A GCEForwardingrule object or None.
    :rtype: :class: `GCEForwardingrule` or None
    """
    try:
        # Does the Target Proxy already exist?
        # TODO(supertom): not all rules are global
        return gce.ex_get_forwarding_rule(name=name, global_rule=global_rule)

    except ResourceNotFoundError:
        return None

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
    
def create_forwardingrule(gce, params):
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

    # TODO(supertom): other targets
    target = get_targethttpproxy(gce, params['target'])
    address = get_address(gce, params['address'], region=params['region'])
    # TODO(supertom): not everything is global
    forwardingrule = gce.ex_create_forwarding_rule(
        name=params['name'], target=target, address=address,
        port_range=params['port_range'], global_rule=True)

    if forwardingrule:
        changed = True
        return_data = { 'name': params['name'], 'forwardingrule': forwardingrule.name }

    return (changed, return_data)

def delete_forwardingrule(forwardingrule):
    """
    Delete a Forwardingrule.
    """
    changed = False
    return_data = []
    if forwardingrule.destroy():
        changed = True
        return_data = True
    return (changed, return_data)

def main():
    module = AnsibleModule(argument_spec=dict(
        name=dict(required=True),
        state=dict(choices=['absent', 'present'], default='present'),
        target=dict(required=True),
        address=dict(required=True),
        region=dict(required=True),
        port_range=dict(required=True),
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
    params['port_range'] = module.params.get('port_range')
    params['address'] = module.params.get('address')
    params['target'] = module.params.get('target')
    params['region'] = module.params.get('region')

    changed = False
    json_output = {'state': params['state']}
    forwardingrule = get_forwardingrule(gce, params['name'])

    if not forwardingrule:
        if params['state'] == 'absent':
            # Doesn't exist in GCE, and state==absent.
            changed = False
            module.fail_json(
                msg="Cannot delete unknown forwardingrule: %s" %
                (params['name']))
        else:
            # Create
            (changed, json_output['forwardingrule']) = create_forwardingrule(gce,
                                                             params)
    elif params['state'] == 'absent':
        # Delete
        (changed, json_output['forwardingrule']) = delete_forwardingrule(forwardingrule)
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
