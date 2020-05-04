#!/usr/bin/env python3

from aws_cdk import core

from ec2_instance.ec2_instance_stack import Ec2InstanceStack


app = core.App()
Ec2InstanceStack(app, "ec2-instance")

app.synth()
