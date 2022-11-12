from pulumi_aws import autoscaling
from settings import cluster_name, target_nginx_connections_waiting, target_openfs
from autoscaling_group import demo_autoscaling_group

"""
Constructs Scaling Policies
"""

# Define target tracking scaling policies:
nginx_tracking_policy = autoscaling.Policy("demo-nginx-tracking-policy",
    autoscaling_group_name=demo_autoscaling_group.name,
    estimated_instance_warmup=10,
    policy_type="TargetTrackingScaling",
    target_tracking_configuration=autoscaling.PolicyTargetTrackingConfigurationArgs(
        target_value=target_nginx_connections_waiting,
        disable_scale_in=False,
        customized_metric_specification=autoscaling.PolicyTargetTrackingConfigurationCustomizedMetricSpecificationArgs(
            metric_name="nginx_connections_waiting",
            namespace=f"{cluster_name}_Prometheus",
            statistic="Average",
            unit="Count",
            metric_dimensions=[
                autoscaling.PolicyTargetTrackingConfigurationCustomizedMetricSpecificationMetricDimensionArgs(
                    name="AutoScalingGroupName",
                    value=f"{cluster_name}"
                )
            ]
        )
    )
)

openfs_tracking_policy = autoscaling.Policy("demo-openfs-tracking-policy",
    autoscaling_group_name=demo_autoscaling_group.name,
    estimated_instance_warmup=10,
    policy_type="TargetTrackingScaling",
    target_tracking_configuration=autoscaling.PolicyTargetTrackingConfigurationArgs(
        target_value=target_openfs,
        disable_scale_in=False,
        customized_metric_specification=autoscaling.PolicyTargetTrackingConfigurationCustomizedMetricSpecificationArgs(
            metric_name="process_open_fds",
            namespace=f"{cluster_name}_Prometheus",
            statistic="Average",
            unit="Count",
            metric_dimensions=[
                autoscaling.PolicyTargetTrackingConfigurationCustomizedMetricSpecificationMetricDimensionArgs(
                    name="AutoScalingGroupName",
                    value=f"{cluster_name}"
                )
            ]
        )
    )
)