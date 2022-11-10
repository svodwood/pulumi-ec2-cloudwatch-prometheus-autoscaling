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

demo_vpc_cidr = "10.200.0.0/16"

demo_public_subnet_cidrs = [
    "10.200.0.0/20",
    "10.200.16.0/20"
]
demo_private_subnet_cidrs = [
    "10.200.32.0/20",
    "10.200.48.0/20"
]