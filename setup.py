import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="ec2_instance",
    version="0.0.1",

    description="Create EC2 instance with SSM management role",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "ec2_instance"},
    packages=setuptools.find_packages(where="ec2_instance"),

    install_requires=[
        "aws-cdk.core==1.36.1",
        "aws-cdk.aws_ec2",
        "aws-cdk.aws_iam",
        "aws-cdk.aws_ssm",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
