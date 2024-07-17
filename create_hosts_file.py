import requests
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
import pynetbox
import credentials


# Define your NetBox API URL and token
API_URL = credentials.api_url
API_TOKEN = credentials.api_token

# Initialize the NetBox API
nb = pynetbox.api(API_URL, token=API_TOKEN)


# Function to strip CIDR prefix from IP address
def strip_cidr(ip_address):
    return ip_address.split('/')[0] if '/' in ip_address else ip_address


# Function to handle None values
def handle_none(value):
    return value if value is not None else ''


def create_hosts_dict(devices):
    hosts = defaultdict(dict)

    for device in devices:
        if device.primary_ip:
            hostname = device.name
            groups = []

            # Add site name to groups
            site_name = handle_none(device.site.name).lower()
            if site_name:
                groups.append(site_name)

            # Add tags to groups
            for tag in device.tags:
                if tag.name == 'ios':
                    groups.append('ios')
                elif tag.name == 'junos':
                    groups.append('junos')
                else:
                    continue

            # Retrieve device-specific data
            data = {
                'mgmt_ip': strip_cidr(device.primary_ip.address),
                'vendor': handle_none(device.device_type.manufacturer.name if device.device_type.manufacturer else None),
                'device_type': handle_none(device.device_type.model),
                'site_code': site_name,
            }

            # Create the host entry
            hosts[hostname] = {
                'hostname': hostname,
                'groups': groups,
                'data': data
            }

    return hosts


# Function to render the Jinja2 template
def render_template(template_file, context):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    return template.render(context)


# Function to write hosts dictionary to a YAML file using Jinja2
def write_hosts_yaml(hosts, template_file='templates/hosts_template.j2', output_file='inventory/hosts.yaml'):
    context = {'hosts': hosts}
    rendered_yaml = render_template(template_file, context)
    with open(output_file, 'w') as file:
        file.write(rendered_yaml)


def main():
    try:
        devices = nb.dcim.devices.filter(role='switch')
        hosts = create_hosts_dict(devices)
        write_hosts_yaml(hosts)
        print("Hosts file created successfully: hosts.yaml")
    except Exception as e:
        print(f"Error fetching data from NetBox API: {e}")
        

if __name__ == '__main__':
    main()
