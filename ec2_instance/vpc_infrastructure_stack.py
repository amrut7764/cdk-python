from aws_cdk import (
    aws_ec2 as _ec2,
    core,
)


class VpcInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Subnet configuration for public, private subnets
        web_subnets = _ec2.SubnetConfiguration(
            subnet_type=_ec2.SubnetType.PUBLIC, cidr_mask=20,
            name="web-"
        )

        # If SubnetType specified as PRIVATE it will create NATGW in each AZ
        reserved_subnets = _ec2.SubnetConfiguration(
            subnet_type=_ec2.SubnetType.ISOLATED,
            cidr_mask=20, name="reserved-"
        )

        db_subnets = _ec2.SubnetConfiguration(
            subnet_type=_ec2.SubnetType.ISOLATED,
            cidr_mask=20,
            name="db-"
        )
        # FIXME How to create custom RouteTable

        # VPC creation
        my_vpc = _ec2.Vpc(
            self, "my_vpc", max_azs=3,
            subnet_configuration=[web_subnets, reserved_subnets, db_subnets],
            cidr="10.16.0.0/16")
