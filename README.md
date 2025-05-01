# AWS Network Automation with Python.

Welcome to the AWS Network Automation with Python project! 🚀 This script is designed to automate the creation of a fully functional AWS network environment using Python and the AWS SDK (boto3). Whether you're a cloud enthusiast, a DevOps engineer, or just someone looking to simplify AWS networking tasks, this project has you covered.

>[!IMPORTANT]
>
>This script is intended for educational and testing purposes. Be mindful of AWS costs when creating resources, and clean up resources when you're done to avoid unnecessary charges. 

## What Does This Script Do?

This Python script automates the following tasks:

1. Key Pair Creation 🔑
    - Generates an SSH key pair to securely access EC2 instances.

2. Dynamic Public IP Fetching 🌐
    - Dynamically fetches your public IP to configure secure access.

3. VPC Creation 🏗️
    - Creates a Virtual Private Cloud (VPC) with a custom CIDR block.

4. Subnet Setup 🌍

    - Public Subnet: Configured with auto-assigned public IPs for internet-facing resources.
    - Private Subnet: Isolated for internal resources.
5. Internet Gateway and Routing 🌐

    - Attaches an Internet Gateway to the VPC.
    - Configures public and private route tables for proper traffic flow.
6. Security Group Configuration 🔒
    - Creates a security group with inbound rules for SSH access.

7. EC2 Instance Deployment 🖥️
    - Launches an EC2 instance in the public subnet, ready for SSH access.

8. DNS Support and Hostnames 🧭
    - Enables DNS support and hostnames for the VPC.

9. Cleanup of Default Route Table 🗑️
    - Replaces the default main route table with a custom one and deletes the default.


## Why Use This Project?

Setting up AWS networking manually can be time-consuming and error-prone. This script automates the entire process, ensuring consistency and saving you valuable time. It's perfect for:

- Learning AWS networking concepts.
- Quickly setting up a test environment.
- Automating repetitive tasks in your cloud infrastructure.

## How to Use

1. Clone This repository to your local machine.
2. Create a python environment to install dependencies
3. Install the required Python dependencies:
``` console 
pip install -r requirements.txt
```
4. Ensure your AWS credentials are configured (using AWS CLI)
5. Change "dry_run = True" --> "dry_run = False" to avoid testing
6. In your python env run the script:
``` console
python main.py
```
7. Wait for the script to complete!

## Notes

- Replace the AMI ID int he scirpt with a valid one for your AWS region
- Ensure you have the neccessary permissions in your AWS account to create resources.

##

Enjoy automating your AWS networking tasks! 🎉

