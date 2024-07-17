# netbox_nornir_gen_hosts
Generates a nornir hosts file from netbox.

To populate correctly, tag devices in netbox with either "junos" or "ios". This can easily be extended for other vendors.
YAML file output can be customised via the jinja2 template.
