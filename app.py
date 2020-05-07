#!/usr/bin/env python3

from aws_cdk import core
from ec2_instance_stack import Ec2InstanceStack
from vpc_infrastructure_stack import VpcInfrastructureStack
import os

env = {
    'account': os.environ['CDK_DEFAULT_ACCOUNT'],
    'region': os.environ['CDK_DEFAULT_REGION']
}

app = core.App()
Ec2InstanceStack(app, "ec2-instance", env=env)
VpcInfrastructureStack(app, "vpc-infrastructure", env=env)

app.synth()
