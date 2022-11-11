import pulumi
from pulumi_aws import lb
from vpc import demo_vpc, demo_public_subnets, demo_private_subnets, demo_sg
from settings import general_tags

"""
Creates a demo AWS Application Load Balancer
"""

# Create a load balancer:
demo_alb = lb.LoadBalancer("demo-alb",
    internal=False,
    load_balancer_type="application",
    security_groups=[demo_sg.id],
    subnets=demo_public_subnets,
    enable_deletion_protection=False,
    tags={**general_tags, "Name": "demo-alb"}
)

# Create a target group:
demo_target_group = lb.TargetGroup("demo-target-group",
    port=80,
    protocol="HTTP",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": "demo-alb"},
    health_check=lb.TargetGroupHealthCheckArgs(
        enabled=True,
        healthy_threshold=3,
        interval=10,
        protocol="HTTP",
        port="80"
    ),
    opts=pulumi.ResourceOptions(parent=demo_alb)
)

# Create a listener:
demo_listener = lb.Listener("demo-listener",
    load_balancer_arn=demo_alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=demo_target_group.arn,
    )],
    opts=pulumi.ResourceOptions(parent=demo_alb)
)