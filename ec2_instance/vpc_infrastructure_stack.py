from aws_cdk import (
    aws_ec2 as _ec2,
    core,
)
import hashlib


class VpcInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._ip_range = 0

        # Crete a custom VPC
        id = hashlib.md5(f'VPC'.encode()).hexdigest()
        vpc = _ec2.CfnVPC(
            self,
            f'vpc-{id}',
            cidr_block='10.0.0.0/16',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            instance_tenancy=None,
            tags=[{'key': 'Name', 'value': 'My Lab VPC'}]
        )

        # TODO IPv6WorkAround for subnet cidr allocation.
        # https://github.com/aws/aws-cdk/issues/894#issuecomment-606140766
        id = hashlib.md5(f'ipv6cidrblock'.encode()).hexdigest()
        assign_ipv6 = _ec2.CfnVPCCidrBlock(self, f'ipv6cidr-{id}', vpc_id=vpc.ref,
                                           amazon_provided_ipv6_cidr_block=True)

        # Create an Internet Gateway and attach it to the VPC
        id = hashlib.md5(f'IGWVPC'.encode()).hexdigest()
        igw = _ec2.CfnInternetGateway(self,
                                      id=f'igw-{id}',
                                      tags=[
                                          {'key': 'Name', 'value': 'My Lab IGW'}]
                                      )
        igw_vpc_attach = _ec2.CfnVPCGatewayAttachment(self, id=f'IGWVPCAttach-{id}',
                                                      vpc_id=vpc.ref,
                                                      internet_gateway_id=igw.ref)

        # Need to create 3 subnets per tier and attach it to custom route table
        for sub_type in ["web", "reserved", "db"]:
            id = hashlib.md5(f'RouteTable-{sub_type}'.encode()).hexdigest()
            route_table = _ec2.CfnRouteTable(self,
                                             f'rtb-{id}',
                                             vpc_id=vpc.ref,
                                             tags=[
                                                 {'key': 'Name', 'value': f'RouteTable-{sub_type}'}])

            # Create Route to internet via IGW for Web Subnets
            if sub_type == 'web':
                route_to_internet = _ec2.CfnRoute(self, f'routetointernet-{id}',
                                                  route_table_id=route_table.ref,
                                                  destination_cidr_block='0.0.0.0/0',
                                                  gateway_id=igw.ref)

            for i in range(0, 3):
                id = hashlib.md5(f'Subnet-{sub_type}{i}'.encode()).hexdigest()
                subnet = _ec2.CfnSubnet(
                    self,
                    id=f'subnet-{id}',
                    cidr_block=f'10.0.{self._ip_range}.0/20',
                    vpc_id=vpc.ref,
                    availability_zone=core.Fn.select(
                        i, core.Fn.get_azs(core.Aws.REGION)),
                    tags=[
                        {'key': 'Name', 'value': f'Subnet-{sub_type}{i + 1}'}])

                self._ip_range = self._ip_range + 16

                # Associate subnets with RouteTable
                id = hashlib.md5(
                    f'RouteTableAssoc-{sub_type}{i}'.encode()).hexdigest()
                route_table_association = _ec2.CfnSubnetRouteTableAssociation(
                    self,
                    f'rtbassoc-{id}',
                    route_table_id=route_table.ref,
                    subnet_id=subnet.ref,
                )
