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
module: rgs_updater
version_added: "2.4"
short_description: Update RGS proxy
requirements:
  - "python >= 2.6"
notes:
  - TODO(supertom):
author:
  - "Tom Melendez (@supertom) <tom@supertom.com>"

'''

EXAMPLES = '''
- name: Update RGS
  rgs_updater
    configuration_file: 
    configuration_type: camera
    validate: yes
    state: present
'''

RETURN = '''
'''

# import module snippets
import ansible.module_utils.six.moves.urllib.parse as urlparse
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec=dict(
        configuration_file=dict(type='path', required=True),
        state=dict(choices=['absent', 'present'], default='present'),
        validate=dict(required=True),
        configuration_type=dict(choices=['camera', 'power', 'antenna'], required=True), ), )


    configuration_file = module.params.get('configuration_file')
    configuration_type = module.params.get('configuration_type')
    state = module.params.get('state')
    validate = module.params.get('validate')
    json_output = {}
    changed = False
    if configuration_type == 'camera':
        import ConfigParser
        config = ConfigParser.RawConfigParser()
        config.read(configuration_file)

        cameraA = config.get('camera-params', 'cameraA')
        cameraB = config.get('camera-params', 'cameraB')
        cameraC = config.get('camera-params', 'cameraC')

        import base64
        cam_encoded = base64.b64encode('%s/%s/%s' % (cameraA, cameraB, cameraC))

        json_output['request_status'] = '200 OK'
        json_output['request_host'] = 'rgs-proxy.central1.spacebox'
        json_output['encoded_data'] = cam_encoded
        changed = True

    json_output['changed'] = changed
    json_output.update(module.params)
    module.exit_json(**json_output)

if __name__ == '__main__':
    main()
