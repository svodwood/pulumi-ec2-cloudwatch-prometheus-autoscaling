from user_data import demo_webserver_user_data_b64
from pulumi_aws import ec2, iam, autoscaling
from settings import ssh_key_name, general_tags, cluster_name
from vpc import demo_sg, demo_private_subnets, demo_s3_endpoint
from alb import demo_target_group
import json
from pulumi import ResourceOptions

"""
Creates EC2 configuration: launch template, autoscaling group and scaling policies
"""
# Fetch a Amazon Linux 2 AMI
demo_ami = ec2.get_ami(most_recent=True,
    filters=[
        ec2.GetAmiFilterArgs(
            name="name",
            values=["amzn2-ami-kernel-5.10-*"],
        ),
        ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
        ec2.GetAmiFilterArgs(
            name="root-device-type",
            values=["ebs"],
        ),
        ec2.GetAmiFilterArgs(
            name="architecture",
            values=["x86_64"]
        )
    ],
    owners=["amazon"]
)

# Create an EC2 instance profile for our demo instances:
aws_managed_instance_profile_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
]

demo_instance_role = iam.Role("demo-instance-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Sid": "",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
        }],
    }),
    tags={**general_tags, "Name": "demo-instance-role"}
)

for i, policy_arn in enumerate(aws_managed_instance_profile_policy_arns):
    demo_role_policy_attachment = iam.RolePolicyAttachment(f"demo-role-policy-attachment-{i}",
        role=demo_instance_role.name,
        policy_arn=policy_arn
    )

demo_instance_profile = iam.InstanceProfile("demo-instance-profile", role=demo_instance_role.name)

# Create an autoscaling group launch template
demo_launch_template = ec2.LaunchTemplate("demo-launch-template",
    key_name=ssh_key_name,
    instance_type="t3.small",
    iam_instance_profile=ec2.LaunchTemplateIamInstanceProfileArgs(
        name=demo_instance_profile.name
    ),
    image_id=demo_ami.image_id,
    vpc_security_group_ids=[demo_sg.id],
    tags={**general_tags, "Name": "demo-launch-template"},
    user_data=demo_webserver_user_data_b64,
    update_default_version=True,
    tag_specifications=[ec2.LaunchTemplateTagSpecificationArgs(
        resource_type="instance",
        tags={**general_tags, "Name": "demo-workload"}
    )],
    opts=ResourceOptions(depends_on=[demo_s3_endpoint])
)

demo_autoscaling_group = autoscaling.Group("demo-autoscaling-group",
    max_size=8,
    min_size=2,
    name=cluster_name,
    enabled_metrics=["GroupMinSize","GroupMaxSize","GroupDesiredCapacity","GroupInServiceInstances","GroupPendingInstances","GroupStandbyInstances","GroupTerminatingInstances","GroupTotalInstances"],
    vpc_zone_identifiers=demo_private_subnets,
    launch_template=autoscaling.GroupLaunchTemplateArgs(
        id=demo_launch_template.id,
        version=demo_launch_template.latest_version
    ),
    default_instance_warmup=10,
    instance_refresh=autoscaling.GroupInstanceRefreshArgs(
        strategy="Rolling",
        preferences=autoscaling.GroupInstanceRefreshPreferencesArgs(
            min_healthy_percentage=50
        ),
        triggers=["tag"],
    ),
    tags=[autoscaling.GroupTagArgs(
        key="Name",
        value="demo-workload-node",
        propagate_at_launch=True
    )],
    opts=ResourceOptions(ignore_changes=["target_group_arns"])
)

demo_autoscaling_group_attachment = autoscaling.Attachment("demo-autoscaling-attachment",
    autoscaling_group_name=demo_autoscaling_group,
    lb_target_group_arn=demo_target_group.arn
)