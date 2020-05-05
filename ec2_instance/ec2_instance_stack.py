from aws_cdk import (
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_ssm as _ssm,
    aws_cloudwatch as _cw,
    core,
)

"""[This code is to creat an EC2 instance with SSM management role attached]
Required Parameters:
    [VPC ID] - Create a SSM parameter store non-secure\
        string with "/cdk/ec2/vpc_id"
    [Instance Type] - Create a SSM parameter store\
         non-secure string with "/cdk/ec2/instance_type"
    [Key Pair Name] - Create a SSM parameter\
         store non-secure string with "/cdk/ec2/key_name"
    [SSH CIDR] - Create a SSM parameter store\
         non-secure string with "/cdk/ec2/sshLocation"
        example: 10.10.0.0/16 or 10.10.10.1/32
    [CDK_DEFAULT_REGION] - Set environment variables on command prompt
     using export for the stack
    CDK_DEFAULT_ACCOUNT] - https://github.com/aws/aws-cdk/issues/4846
"""

# Read User Data from user_data directory
with open("./user_data/user_data.sh") as f:
    user_data = f.read()
    user_data = core.Fn.sub(user_data)


class Ec2InstanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # read parameters from SSM
        vpcid = _ssm.StringParameter.value_from_lookup(self, "/cdk/ec2/vpc_id")

        instance_type = _ssm.StringParameter.value_from_lookup(
            self,
            "/cdk/ec2/instance_type"
        )

        key_name = _ssm.StringParameter.value_from_lookup(
            self, "/cdk/ec2/key_name"
        )

        allow_ssh_web_location = _ssm.StringParameter.value_from_lookup(
            self, "/cdk/ec2/sshLocation"
        )

        # Get the existing VPC
        my_vpc = _ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=vpcid
        )

        # Prepare security group configuration - create security group
        my_security_group = _ec2.SecurityGroup(
            self, "my_security_group", vpc=my_vpc,
            security_group_name="myfirstcdk_secgroup")

        # Add an ingress rules for above security group
        add_securitygroup_ingress_for_22 = my_security_group.add_ingress_rule(
            peer=_ec2.Peer.ipv4(allow_ssh_web_location),
            connection=_ec2.Port.tcp(22)
        )

        add_securitygroup_ingress_for_80 = my_security_group.add_ingress_rule(
            peer=_ec2.Peer.ipv4(allow_ssh_web_location),
            connection=_ec2.Port.tcp(80)
        )

        # create an IAM role with ssm managed policy
        managed_policies = _iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonSSMManagedInstanceCore"
        ),

        my_session_mgmt_role = _iam.Role(
            self, id="my_session_mgmt_role",
            assumed_by=_iam.ServicePrincipal(
                service="ec2.amazonaws.com"),
            description="SSM session management role",
            managed_policies=list(
                managed_policies),
            role_name="SessionManagerRole"
        )

        # Create an EC2 instance with the above configuration
        ec2_instance = _ec2.Instance(
            self, "my_ec2_instance",
            instance_type=_ec2.InstanceType(
                instance_type_identifier=instance_type),
            machine_image=_ec2.MachineImage.latest_amazon_linux(),
            vpc=my_vpc, instance_name="MyInstance",
            key_name=key_name, security_group=my_security_group,
            role=my_session_mgmt_role,
            user_data=_ec2.UserData.custom(user_data)
        )

        # Create a CloudWatch Alarm for EC2 instance CPU utilization
        metric = _cw.Metric(metric_name="CPUUtilization", namespace="AWS/EC2",
                            dimensions={
                                "InstanceId": ec2_instance.instance_id,
                            },
                            statistic="Average"
                            )

        cpu_alarm = _cw.Alarm(
            self, "cpu_alarm", alarm_name="CPUUtilizationOver15",
            alarm_description="CPU Utilization Over 15 Percent",
            evaluation_periods=3, threshold=15,
            period=core.Duration.seconds(60),
            metric=metric, datapoints_to_alarm=2,
            comparison_operator=_cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )

        # CFN outputs
        ec2_instance_id = core.CfnOutput(
            self, "instance_id", value=ec2_instance.instance_id,
            description="InstanceId of the newly created EC2 instance")

        availability_zone = core.CfnOutput(
            self, "availability zone",
            value=ec2_instance.instance_availability_zone,
            description="Availability Zone of the newly created EC2")

        public_dns_name = core.CfnOutput(
            self, "public_dns_name",
            value=ec2_instance.instance_public_dns_name,
            description="Public DNSName of the newly created EC2 instance"
        )

        public_ip = core.CfnOutput(
            self, "public_ip",
            value=ec2_instance.instance_public_ip,
            description="Public IP address of the newly created EC2"
        )

        cloudwatch_alarm = core.CfnOutput(
            self, "Cloudwatch Alarm",
            value=cpu_alarm.alarm_arn,
            description="CPU alarm ARN")
