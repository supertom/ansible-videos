# space-image-site

## Create Cross Region Infrastructure

`ansible-playbook space-image-site/space-image-site.yml -vvv | tee /tmp/space-site.log`

## Cleanup

`ansible-playbook space-image-site/cleanup.yml -vvv | tee /tmp/space-site.log`

## Generate Traffic

`while true; do curl -D - http://<IP ADDRESS>; done`

## View console

https://console.cloud.google.com/networking/loadbalancing/advanced/backendServices/details/iva-bes?project=spacebox-cloud