from jinja2 import Template
import json
from pulumi_aws import ssm
from settings import cluster_name, general_tags, cwa_settings_parameter_path, cwa_prometheus_parameter_path 
import yaml

"""
Constructs objects for the CWA configuration
"""

# Cloudwatch Agent configuration, written to SSM parameter store:
demo_cwa_configuration = json.dumps({
	"agent":{
		"metrics_collection_interval":60
	},
	"logs":{
		"metrics_collected":{
			"prometheus":{
				"cluster_name":f"{cluster_name}",
				"log_group_name":f"{cluster_name}Prometheus",
				"prometheus_config_path":"/opt/aws/amazon-cloudwatch-agent/etc/prometheus.yml",
				"emf_processor":{
					"metric_declaration_dedup":True,
					"metric_namespace":f"{cluster_name}_Prometheus",
					"metric_unit":{
						"process_open_fds":"Count",
						"nginx_connections_waiting":"Count"
					},
					"metric_declaration":[
						{
							"source_labels":[
								"origin"
							],
							"label_matcher":"^web-server-node-exporter$",
							"dimensions":[
								[
									"AutoScalingGroupName",
									"node"
								],
								[
									"AutoScalingGroupName"
								]
							],
							"metric_selectors":[
								"^process_open_fds$"
							]
						},
						{
							"source_labels":[
								"origin"
							],
							"label_matcher":"^web-server-nginx$",
							"dimensions":[
								[
									"AutoScalingGroupName",
									"node"
								],
								[
									"AutoScalingGroupName"
								]
							],
							"metric_selectors":[
								"^nginx_connections_waiting$"
							]
						}
					]
				}
			}
		}
	},
	"metrics":{
		"namespace":f"{cluster_name}_Memory",
		"append_dimensions":{
			"AutoScalingGroupName":"${aws:AutoScalingGroupName}",
			"node":"${aws:InstanceId}"
		},
		"aggregation_dimensions":[
			[
				"AutoScalingGroupName"
			]
		],
		"metrics_collected":{
			"mem":{
				"measurement":[
					{
						"name":"mem_used_percent",
						"rename":"MemoryUtilization",
						"unit":"Percent"
					}
				],
				"metrics_collection_interval":60
			}
		}
	}
})

demo_ssm_cwa_configuration_parameter = ssm.Parameter("demo-cwa-config",
    type="String",
    data_type="text",
    name=cwa_settings_parameter_path,
    tags={**general_tags, "Name": "demo-cwa-config"},
    value=demo_cwa_configuration
)

# Cloudwatch Agent prometheus scrape configuration, written to SSM parameter store:
demo_prometheus_configuration_template = Template("""
global:
  scrape_interval: 1m
  scrape_timeout: 10s
scrape_configs:
  - job_name: Local_NodeExporter_Metrics
    static_configs:
      - targets:
          - 'localhost:9100'
        labels:
          origin: web-server-node-exporter
          AutoScalingGroupName: {{autoscaling_group_name}}
  - job_name: Local_Nginx_Metrics
    static_configs:
      - targets:
          - 'localhost:9113'
        labels:
          origin: web-server-nginx
          AutoScalingGroupName: {{autoscaling_group_name}}
""")

demo_prometheus_configuration = demo_prometheus_configuration_template.render(autoscaling_group_name=cluster_name)

demo_ssm_cwa_promscrape_configuration_parameter = ssm.Parameter("demo-cwa-prom-config",
    type="String",
    data_type="text",
    name=cwa_prometheus_parameter_path,
    tags={**general_tags, "Name": "demo-cwa-prom-config"},
    value=demo_prometheus_configuration
)