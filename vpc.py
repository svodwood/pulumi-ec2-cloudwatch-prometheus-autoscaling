import pulumi
from pulumi_aws import ec2, config, get_availability_zones
from settings import general_tags, demo_vpc_cidr, demo_private_subnet_cidrs, demo_public_subnet_cidrs

"""
Creates a minium of AWS networking objects required for the demo stack to work
"""

# Create a VPC and Internet Gateway:
demo_vpc = ec2.Vpc("demo-vpc",
    cidr_block=demo_vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**general_tags, "Name": f"demo-vpc-{config.region}"}
)

demo_igw = ec2.InternetGateway("demo-igw",
    vpc_id=demo_vpc.id,
    tags={**general_tags, "Name": f"demo-igw-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Create a default any-any security group for demo purposes:
demo_sg = ec2.SecurityGroup("demo-security-group",
    description="Allow any-any",
    vpc_id=demo_vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="Any",
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    tags={**general_tags, "Name": f"demo-sg-{config.region}"},
    opts=pulumi.ResourceOptions(parent=demo_vpc)
)

# Create subnets:
demo_azs = get_availability_zones(state="available").names
demo_public_subnets = []
demo_private_subnets = []

for i in range(2):
    prefix = f"{demo_azs[i]}"
    
    demo_public_subnet = ec2.Subnet(f"demo-public-subnet-{prefix}",
        vpc_id=demo_vpc.id,
        cidr_block=demo_public_subnet_cidrs[i],
        availability_zone=demo_azs[i],
        tags={**general_tags, "Name": f"demo-public-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_public_subnets.append(demo_public_subnet)

    demo_public_route_table = ec2.RouteTable(f"demo-public-rt-{prefix}",
        vpc_id=demo_vpc.id,
        tags={**general_tags, "Name": f"demo-spoke-rt-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )
    
    demo_public_route_table_association = ec2.RouteTableAssociation(f"demo-public-rt-association-{prefix}",
        route_table_id=demo_public_route_table.id,
        subnet_id=demo_public_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )

    demo_public_wan_route = ec2.Route(f"demo-public-wan-route-{prefix}",
        route_table_id=demo_public_route_table.id,
        gateway_id=demo_igw.id,
        destination_cidr_block="0.0.0.0/0",
        opts=pulumi.ResourceOptions(parent=demo_public_subnet)
    )

    demo_eip = ec2.Eip(f"demo-eip-{prefix}",
        tags={**general_tags, "Name": f"demo-eip-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_nat_gateway = ec2.NatGateway(f"demo-nat-gateway-{prefix}",
        allocation_id=demo_eip.id,
        subnet_id=demo_public_subnet.id,
        tags={**general_tags, "Name": f"demo-nat-{prefix}"},
        opts=pulumi.ResourceOptions(depends_on=[demo_vpc])
    )

    demo_private_subnet = ec2.Subnet(f"demo-private-subnet-{prefix}",
        vpc_id=demo_vpc.id,
        cidr_block=demo_private_subnet_cidrs[i],
        availability_zone=demo_azs[i],
        tags={**general_tags, "Name": f"demo-private-subnet-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_vpc)
    )
    
    demo_private_subnets.append(demo_private_subnet)

    demo_private_route_table = ec2.RouteTable(f"demo-private-rt-{prefix}",
        vpc_id=demo_vpc.id,
        tags={**general_tags, "Name": f"demo-private-rt-{prefix}"},
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )
    
    demo_private_route_table_association = ec2.RouteTableAssociation(f"demo-private-rt-association-{prefix}",
        route_table_id=demo_private_route_table.id,
        subnet_id=demo_private_subnet.id,
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )

    demo_private_wan_route = ec2.Route(f"demo-private-wan-route-{prefix}",
        route_table_id=demo_private_route_table.id,
        nat_gateway_id=demo_nat_gateway.id,
        destination_cidr_block="0.0.0.0/0",
        opts=pulumi.ResourceOptions(parent=demo_private_subnet)
    )

# Create an S3 endpoint to save money on NAT traffic:
demo_s3_endpoint = ec2.VpcEndpoint("demo-s3-endpoint",
    vpc_id=demo_vpc.id,
    service_name=f"com.amazonaws.{config.region}.s3",
    vpc_endpoint_type="Interface",
    subnet_ids=demo_private_subnets,
    security_group_ids=[demo_sg.id],
    tags={**general_tags, "Name": f"demo-s3-endpoint-{config.region}"})