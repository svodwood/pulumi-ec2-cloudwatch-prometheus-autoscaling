import pulumi

project_config = pulumi.Config()
stack = pulumi.get_stack()
project = pulumi.get_project()

"""
General resource tags.
"""
general_tags = {
    "pulumi-project": f"{project}",
    "pulumi-stack": f"{stack}"
}

"""
Configuration variables from pulumi settings file
"""

ssh_key_name = project_config.require("ssh-key-name")

demo_vpc_cidr = "10.200.0.0/16"

demo_public_subnet_cidrs = [
    "10.200.0.0/20",
    "10.200.16.0/20"
]
demo_private_subnet_cidrs = [
    "10.200.32.0/20",
    "10.200.48.0/20"
]

cluster_name = "demoWebCluster"

cwa_settings_parameter_path = f"/{cluster_name}/cwa_settings_config"
cwa_prometheus_parameter_path = f"/{cluster_name}/cwa_prometheus_config"
nginx_stub_status_config_parameter_path = f"/{cluster_name}/nginx_stub_status_config"

nginx_stub_status_port = "8113"
nginx_config_file_path = "/etc/nginx/conf.d/nginx-status.conf"

# Autoscaling policy targets:

target_nginx_connections_waiting = 2
target_node_sockstat_TCP_inuse = 50