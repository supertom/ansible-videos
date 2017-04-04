#!/usr/bin/python
# TODO(supertom): gcp_url_map IN PROGRESS. NOT WORKING AS WE'RE SWAPPING OUT THE CLIENT.
# Copyright 2017 Google Inc.
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
module: gcp_url_map
version_added: "2.4"
short_description: Create, Update or Destory a Url_Map.
description:
    - Create, Update or Destory a Url_Map. See
      U(https://cloud.google.com/compute/docs/load-balancing/http/url-map) for an overview.
      Full install/configuration instructions for the gce* modules can
      be found in the comments of ansible/test/gce_tests.py.
requirements:
  - "python >= 2.6"
  - "google-api-python-client >= 1.6.2"
  - "google-auth >= 0.9.0"
  - "google-auth-httplib2 >=0.0.2"
notes:
  - TODO(supertom):
author:
  - "Tom Melendez (@supertom) <tom@supertom.com>"
options:
  url_map_name:
    description:
       - Name of the Url_Map.
    required: true
'''

EXAMPLES = '''
- name: Create Minimum Url_Map
  gcp_url_map
    service_account_email: "{{ service_account_email }}"
    credentials_file: "{{ credentials_file }}"
    project_id: "{{ project_id }}"
    url_map_name: my-url_map
    default_service: my-backend-service
    state: present
'''

RETURN = '''
'''


try:
    # TODO(supertom): remove all libcloud related things
    # look at pubsub to see if I can do anything like that.
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

# TODO(supertom): move this
from googleapiclient.errors import HttpError
    
# import module snippets
import ansible.module_utils.six.moves.urllib.parse as urlparse
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.gcp import get_google_api_client

USER_AGENT_PRODUCT = 'ansible-url_map'
USER_AGENT_VERSION = '0.0.1'

def build_host_rules():
    pass

def build_path_matchers():
    pass

def build_url_map(params):
    gcp_dict = params_to_gcp_dict(params, 'url_map_name')
    return gcp_dict
    # build_host_rules()
    # build_path_matchers()
    # pass


def underscore_to_camel(txt):
    return txt.split('_')[0] + ''.join(x.capitalize()
                                       or '_' for x in txt.split('_')[1:])

def remove_non_gcp_params(params):
    """
    TODO(supertom): ensure we're only working on a copy at this point.
    """
    params_to_remove = ['state']
    for p in params_to_remove:
        if p in params:
            del params[p]

    return params

def params_to_gcp_dict(params, resource_name):
    """
    convert params to gcp dict
    specifically, snake to camelCase
    ex: default_service to defaultService
    special provision for the resource name
    build urls for services?
    """
    gcp_dict = {}
    params = remove_non_gcp_params(params)
    for k, v in params.items():
        gcp_key = underscore_to_camel(k)
        gcp_dict[gcp_key] = v
        # TODO(supertom): be more determinstic here
        if k == resource_name:
            gcp_dict['name'] = v

    return gcp_dict
        

def parse_gcp_url(url):
    """
    /compute/v1/projects/supertom-graphite/global/backendServices/bes
    /SERVICE/'projects'/PROJECT_ID/LOCATION/RESOURCE/RESOURCE_NAME
    # TODO(supertom): possibly handle URLs with just the GCP path
    # LOCATION FORWARD
    """
    p = urlparse(url)
    if not p:
        return None
    else:
        # we add extra items such as
        # zone, region and resource_name
        url_parts = {}
        url_parts['scheme'] = p.scheme
        url_parts['host'] = p.netloc
        url_parts['path'] = p.path
        url_parts['params'] = p.params
        url_parts['fragment'] = p.fragment
        url_parts['query'] = p.query
        url_parts['project'] = None
        url_parts['service'] = None
        url_parts['api_version'] = None
        
        path_parts = p.split('/')
        url_parts['service'] = path_parts[0]
        url_parts['api_version'] = path_parts[1]
        if path_parts[2] == 'projects':
            url_parts['project'] = path_parts[3]
        location_type = path_parts[4]
        if location_type == 'regions':
            url_parts['region'] = path_parts[5]
        elif location_type == 'zones':
            url_parts['zone'] = path_parts[5]
        else:
            url_parts['global'] = True

        # TODO(supertom): should be more robust
        url_parts['resource_name'] = url_parts[-1]
            
        return url_parts

def fetch_response(req, raw=True):
    """
    General fetching function for list.
    TODO(supertom): make this more generic
    """
    try:
        resp = req.execute()
        if raw:
            return resp
        else:
            if 'items' in resp:
                return resp['items']
            else:
                return None
    except HttpError as h:
        if h.resp.status == 404:
            return None
        else:
            raise
    except Exception:
        raise
    

def get_url_map(client, name, project_id=None):
    """
    Get a Url_Map from GCE.
    TODO(supertom): docs are wrong.

    :param gce: An initialized GCE driver object.
    :type gce:  :class: `GCENodeDriver`

    :param name: Name of the Backend Service.
    :type name:  ``str``

    :return: A GCEUrl_Map object or None.
    :rtype: :class: `GCEUrl_Map` or None
>>> from apiclient.discovery import build
>>> service = build('compute', 'v1')
>>> req = service.url_maps().get(project='supertom-graphite', url_map='testurl_map')
>>> resp = req.execute()
>>> print resp
    """
    try:
        req = client.urlMaps().get(project=project_id, urlMap=name)
        return fetch_response(req)
    except:
        raise

def create_url_map(client, params, project_id):
    """
    Create a new Url Map.
    TODO(supertom): all docs NG.

    :param client: An initialized Google Compute object
    :type client:  :class: `GCENodeDriver`

    :param params: Dictionary of arguments from AnsibleModule.
    :type params:  ``dict``

    :return: Tuple with changed stats and TODO(supertom): something here.
    :rtype: tuple in the format of (bool, list)
    """
    BACKEND_SERVICE_BASE_PATH='https://www.googleapis.com/compute/v1/projects/%s/global/backendServices' % (project_id)
    changed = False
    gcp_dict = build_url_map(params)
    import os
    gcp_dict['defaultService'] = os.path.join(BACKEND_SERVICE_BASE_PATH, gcp_dict['defaultService'])
    try:
        req = client.urlMaps().insert(project=project_id, body=gcp_dict)
        return_data = fetch_response(req)
        return (True, return_data)
    except:
        raise


def delete_url_map(client, name, project_id):
    """
    Delete a Url_Map.
    """
    changed = False
    try:
        req = client.urlMaps().delete(project=project_id, urlMap=name)
        return_data = fetch_response(req)
        return (True, return_data)
    except:
        raise

def main():
    module = AnsibleModule(argument_spec=dict(
        url_map_name=dict(required=True),
        state=dict(choices=['absent', 'present'], default='present'),
        default_service=dict(required=True),
        service_account_email=dict(),
        service_account_permissions=dict(type='list'),
        pem_file=dict(),
        credentials_file=dict(),
        project_id=dict(), ), )

    if not HAS_PYTHON26:
        module.fail_json(
            msg="GCE module requires python's 'ast' module, python v2.6+")

    client, conn_params = get_google_api_client(module, 'compute', user_agent_product=USER_AGENT_PRODUCT,
                                   user_agent_version=USER_AGENT_VERSION)

    params = {}
    params['state'] = module.params.get('state')
    params['url_map_name'] = module.params.get('url_map_name')
    params['default_service'] = module.params.get('default_service')

    changed = False
    json_output = {'state': params['state']}
    url_map = get_url_map(client,
                          name=params['url_map_name'],
                          project_id=conn_params['project_id'])
#    json_output['url_map'] = url_map

    if not url_map:
        json_output['not_urlmap'] = True
        if params['state'] == 'absent':
            # Doesn't exist in GCE, and state==absent.
            changed = False
            module.fail_json(
                msg="Cannot delete unknown url_map: %s" %
                (params['url_map_name']))
        else:
            # Create
            json_output['try_create'] = True
            (changed, json_output['url_map']) = create_url_map(client,
                                                               params=params,
                                                               project_id=conn_params['project_id'])
    elif params['state'] == 'absent':
        # Delete
        (changed, json_output['url_map']) = delete_url_map(client,
                                                           name=params['url_map_name'],
                                                           project_id=conn_params['project_id'])
    else:
        json_output['try_update'] = True
        # Update
        pass

    json_output['changed'] = changed
    json_output.update(params)
    module.exit_json(**json_output)

if __name__ == '__main__':
    main()
