from jinja2 import Template
from settings import cwa_settings_parameter_path, cwa_prometheus_parameter_path, nginx_stub_status_config_parameter_path, nginx_config_file_path, nginx_stub_status_port
from pulumi_aws import config
import base64

"""
Creates an EC2 instance user data script
"""

# Create a user data bash script template:
demo_webserver_user_data_template = Template("""
#!/bin/bash
yum update -y

# Install CWA
yum install amazon-cloudwatch-agent -y

# Install Nginx and configure the stub status module
amazon-linux-extras install nginx1.12 -y 
aws ssm get-parameter --name {{ nginx_stub_status_config_parameter_path }} --region {{ region }} --output text --query Parameter.Value > {{ nginx_config_file_path }}

# Add a user to run the exporters
useradd --no-create-home metrics_exporter

# Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.4.0/node_exporter-1.4.0.linux-amd64.tar.gz
tar xzf node_exporter-1.4.0.linux-amd64.tar.gz
cp node_exporter-1.4.0.linux-amd64/node_exporter /usr/local/bin/node_exporter
rm -rf node_exporter-1.4.0.linux-amd64.tar.gz node_exporter-1.4.0.linux-amd64

# Create Node Exporter systemd service
cat << 'EOF' > /etc/systemd/system/node-exporter.service
[Unit]
Description=Prometheus Node Exporter Service
After=network.target
[Service]
User=metrics_exporter
Group=metrics_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
[Install]
WantedBy=multi-user.target
EOF

# Install Nginx Exporter
wget https://github.com/nginxinc/nginx-prometheus-exporter/releases/download/v0.11.0/nginx-prometheus-exporter_0.11.0_linux_amd64.tar.gz
tar xzf nginx-prometheus-exporter_0.11.0_linux_amd64.tar.gz
cp nginx-prometheus-exporter /usr/local/bin/nginx-prometheus-exporter
rm -rf nginx-prometheus-exporter_0.11.0_linux_amd64.tar.gz nginx-prometheus-exporter

# Create Nginx Exporter systemd service
cat << 'EOF' > /etc/systemd/system/nginx-prometheus-exporter.service
[Unit]
Description=Prometheus Nginx Exporter Service
After=network.target
[Service]
User=metrics_exporter
Group=metrics_exporter
Type=simple
ExecStart=/usr/local/bin/nginx-prometheus-exporter -nginx.scrape-uri http://127.0.0.1:{{ nginx_stub_status_port }}/metrics -web.listen-address=127.0.0.1:9113
[Install]
WantedBy=multi-user.target
EOF

# Configure CWA
aws ssm get-parameter --name {{ cwa_prometheus_parameter_path }} --region {{ region }} --with-decryption --output text --query Parameter.Value > /opt/aws/amazon-cloudwatch-agent/etc/prometheus.yml
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:"{{ cwa_settings_parameter_path }}" -s

# Start everything up
systemctl daemon-reload
systemctl enable nginx
systemctl start nginx
systemctl enable node-exporter
systemctl start node-exporter
systemctl enable nginx-prometheus-exporter
systemctl start nginx-prometheus-exporter
""")

# Render the user data bash script:
demo_webserver_user_data = demo_webserver_user_data_template.render(
    nginx_stub_status_config_parameter_path=nginx_stub_status_config_parameter_path, 
    region=config.region,
    nginx_config_file_path=nginx_config_file_path,
    nginx_stub_status_port=nginx_stub_status_port,
    cwa_prometheus_parameter_path=cwa_prometheus_parameter_path,
    cwa_settings_parameter_path=cwa_settings_parameter_path
)

# base64 encode the user data bash script:
demo_webserver_user_data_b64 = base64.b64encode(demo_webserver_user_data.encode()).decode()