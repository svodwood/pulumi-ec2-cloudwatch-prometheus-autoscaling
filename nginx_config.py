from jinja2 import Template
from pulumi_aws import ssm
from settings import nginx_stub_status_port, nginx_stub_status_config_parameter_path, general_tags

"""
Creates an nginx config to enable stub status module
"""

demo_nginx_stub_status_configuration_file = Template("""
server {
        listen 127.0.0.1:{{ port }};
        location = /metrics {
                stub_status;
        }
}
""")
demo_nginx_stub_status_configuration = demo_nginx_stub_status_configuration_file.render(port=nginx_stub_status_port)

demo_nginx_configuration_parameter = ssm.Parameter("demo-nginx-config",
    type="String",
    data_type="text",
    name=nginx_stub_status_config_parameter_path,
    tags={**general_tags, "Name": "demo-nginx-config"},
    value=demo_nginx_stub_status_configuration
)