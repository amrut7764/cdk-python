#!/usr/bin/env python3

from ec2_instance.ec2_instance_stack import Ec2InstanceStack
from aws_cdk import core
import os

app = core.App()
Ec2InstanceStack(app, "ec2-instance",
                 env={
                     'account': os.environ['CDK_DEFAULT_ACCOUNT'],
                     'region': os.environ['CDK_DEFAULT_REGION']
                 }
                 )

app.synth()
