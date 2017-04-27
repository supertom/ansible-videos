# Demos

Note: this is demo info only and this readme could be out of date.  Source of truth for the videos is the internal docs and respective scripts.

Required:
* Python modules: google-api-python-client, google-cloud-spanner, google_auth_httplib2
* An image named camera-test-image with the test-camera-params executable is required in the project for the first video
* An image template is required for the second video.
* A port 80 healthcheck called iva-healthcheck is needed for the second video.
* Other: gcp.py placed at lib/ansible/module_utils/gcp.py
* See the 'other' directory for more files that need to be in place.
* Compute Engine API needs to be [enabled.](https://console.cloud.google.com/apis/api/compute-component.googleapis.com/overview)
* Spanner API needs to be [enabled](https://console.cloud.google.com/apis/api/spanner.googleapis.com/overview)

Files to be edited:
- gce_vars/auth - put your project credentials in here
- group_vars/all - username and ssh key location here

## Episode 1
* update-camera-params - launch multiple instances with custom image. Run a test with parameters we send in.  If successful, write ini file and push to Groundstation.

## Episode 2
* space-image-site - create a cross-region load balanced web application.

## Episode 3
* networking - set up networks and firewall rules for our RGS to IPS network and our IPS to IVA network.

## Episode 4
* pubsub-and-spanner - scale out our system by adding pubsub and spanner

## Episode 5
* building-a-module - We've shown the community what's available, now we show them how to contribute.  Specifics on building a Google module.

## Episode 6
* testing-a-module - How to build unit and integration tests for our modules.
