# Other files needed

Local directory /opt/rgs/conf needs to be in place and writable by your user (at least).  An inifile is dropped here during the first demo.

/usr/local/bin/test-camera-params - put this on the image you create for push-camera-params (so, not installed here, but on the image that is required.)

/home/USERNAME/.ansible.cfg - config settings to suppress warnings

/etc/ansible/hosts - put this host file in place to keep the host warning from appearing

Other: gcp.py placed at lib/ansible/module_utils/gcp.py

Instance Template called iva-template needs to be in the project.  The following startup script needs to be set:
```
apt-get update && apt-get install -y apache2; zone=$(curl -s -H "Metadata-flavor: Google" http://metadata/computeMetadata/v1/instance/zone); hostname=$(curl -s -H "Metadata-flavor: Google" http://metadata/computeMetadata/v1/instance/name);echo ${zone}:${hostname} > /var/www/html/index.html

```
