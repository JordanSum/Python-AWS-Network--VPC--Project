import boto3 # For AWS SDK
import requests # For fetching public IP
import os # For creating file operations on local machine

# Create a key pair for SSH access to the EC2 instance. This is now a required step for creating an EC2 instance in AWS.
# This function creates a key pair in AWS EC2 and saves the private key to a file.
def create_key_pair():
    ec2 = boto3.client('ec2')

    try:
        key_name = "PythonKeyPair"
        key_pair = ec2.create_key_pair(KeyName=key_name)
        private_key = key_pair['KeyMaterial']

        # Save the private key to a file named what the variable key_name is set to
        with open(f"{key_name}.pem", "w") as file:
            file.write(private_key)

        # Set permissions for the private key file
        os.chmod(f"{key_name}.pem", 0o400)

        print(f"Key pair {key_name} created and saved as {key_name}.pem")
        return key_name
    except Exception as e:
        print(f"Error creating key pair: {e}")

# Fetch the public IP dynamically
def get_public_ip():
    try:
        response = requests.get("https://checkip.amazonaws.com")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

def create_vpc(key_name, public_ip):
    client = boto3.client('ec2')

    vpc = client.create_vpc(
        CidrBlock="10.0.0.0/16",
        AmazonProvidedIpv6CidrBlock=False,
        InstanceTenancy="default",
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Python_Project_VPC',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        DryRun=dry_run,
    )

    vpc_id = vpc['Vpc']['VpcId']

    # Create a public subnet
    public_subnet = client.create_subnet(
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name', 
                        'Value': 'Python_Project_Subnet_Public',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='us-west-2a',
        DryRun=dry_run,
    )

    # Retrieve the Subnet ID
    public_subnet_id = public_subnet['Subnet']['SubnetId']

    # Enable auto-assign public IP on the public subnet
    client.modify_subnet_attribute(
        SubnetId=public_subnet_id,
        MapPublicIpOnLaunch={
            'Value': True
        }
    )

    # Create a security group for the public subnet
    security_group = client.create_security_group(
        Description='Public subnet security group',
        GroupName='PythonPublicSecurityGroup',
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [
                    {
                        'Key': 'Name', 
                        'Value': 'Python_Project_Public_Security_Group',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        DryRun=dry_run,
    )
    security_group_id = security_group['GroupId']
    
    # Add inbound rules to the security group
    client.authorize_security_group_ingress(
        GroupId = security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [
                    {
                        'CidrIp': f'{public_ip}/32',  # Replace with your public IP
                        'Description': 'SSH access'
                    }
                ],
            }
        ],
        DryRun=dry_run,
    )
# No need to add outbound rules as the default is all traffic allowed in aws


    # Create a private subnet
    private_subnet = client.create_subnet(
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name', 
                        'Value': 'Python_Project_Subnet_Private',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        VpcId=vpc_id,
        CidrBlock='10.0.2.0/24',
        AvailabilityZone='us-west-2b',
        DryRun=dry_run,
    )

    private_subnet_id = private_subnet['Subnet']['SubnetId']

    IGW = client.create_internet_gateway(
        TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [
                    {
                        'Key': 'Name', 
                        'Value': 'Python_Internet_Gateway',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        DryRun=dry_run,
    )

    InternetGatewayId = IGW['InternetGateway']['InternetGatewayId']

    attach_IGW = client.attach_internet_gateway(
        InternetGatewayId=IGW['InternetGateway']['InternetGatewayId'],
        VpcId=vpc_id
    )

    public_route_tables = client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Python_Project_Public_Route_Table',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        DryRun=dry_run,
    )
    public_route_table_id = public_route_tables['RouteTable']['RouteTableId']

    # Add a route to the internet gateway (Place the create_route call after attaching the IGW and before associating the route table with the public subnet. This ensures the route is added before the subnet uses the route table.)

    client.create_route(
        RouteTableId=public_route_table_id,
        DestinationCidrBlock = '0.0.0.0/0',
        GatewayId=IGW['InternetGateway']['InternetGatewayId'],
    )
    
    # Associate the route table with the public subnet
    
    client.associate_route_table(
        RouteTableId=public_route_table_id,
        SubnetId=public_subnet_id,
    )

    # Create a custom route table for the private subnet
    private_route_table = client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Python_Project_Private_RouteTable',
                    },
                    {
                        'Key': 'Project',
                        'Value': 'Networking_Automation'
                    },
                ]
            },
        ],
        DryRun=dry_run,
    )
    private_route_table_id = private_route_table['RouteTable']['RouteTableId']

    # Associate the private route table with the private subnet
    client.associate_route_table(
        RouteTableId=private_route_table_id,
        SubnetId=private_subnet_id,
    )

    # AWS will automatically create a default route table, making three route tables in total. This will delete the third route table.
    # Get the current main route table association
    main_route_table = client.describe_route_tables(
        Filters=[
            {
                'Name': 'association.main',
                'Values': ['true']
            },
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )

    # Extract the RouteTableId and AssociationId of the default main route table
    default_main_route_table_id = main_route_table['RouteTables'][0]['RouteTableId']
    main_route_table_association_id = main_route_table['RouteTables'][0]['Associations'][0]['RouteTableAssociationId']

    # Replace the main route table with the public route table
    client.replace_route_table_association(
        AssociationId=main_route_table_association_id,
        RouteTableId=public_route_table_id
    )
    print(f"Public Route Table {public_route_table_id} set as the main route table for VPC {vpc_id}")

    # Delete the default main route table
    client.delete_route_table(RouteTableId=default_main_route_table_id)
    print(f"Default main route table {default_main_route_table_id} deleted.")

    # Create a ec2 instance in the public subnet
    ec2 = boto3.resource('ec2')
    instance_id = None

    try:
        instance = ec2.create_instances(
            ImageId='ami-087f352c165340ea1',  # Replace with a valid AMI ID
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            SecurityGroupIds=[security_group_id],
            KeyName=key_name,  # Replace with your key pair name in order to SSH into the instance
            SubnetId=public_subnet_id,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'Python_Project_Instance',
                        },
                        {
                            'Key': 'Project',
                            'Value': 'Networking_Automation'
                        },
                    ]
                },
            ],
            DryRun=dry_run,
        )
        instance_id = instance[0].id
    except Exception as e:
        print("Error creating EC2 instance: Instance creation failed.")

    # Wait for the instance to be in the running state
    if instance_id is not None:
        ec2_client = boto3.client('ec2')
        ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])

        # Retrieve the public IP address of the instance
        instance_details = ec2_client.describe_instances(InstanceIds=[instance_id])
        public_ip_address = instance_details['Reservations'][0]['Instances'][0].get('PublicIpAddress')

        if public_ip_address:
            print(f"Public IP Address retrieved for the instance!")
        else:
            print("Instance does not have a public IP address assigned.")
    else:
        print("Instance creation failed. No instance ID returned.")

    return vpc_id, private_subnet_id, public_subnet_id, InternetGatewayId, public_route_table_id, private_route_table_id

def enable_dns_support_and_hostname(vpc_id):
    ec2 = boto3.client('ec2')

    try:
        ec2.modify_vpc_attribute(
            VpcId=vpc_id,
            EnableDnsSupport={
                'Value': True
            }
        )

        ec2.modify_vpc_attribute(
            VpcId=vpc_id,
            EnableDnsHostnames={
                'Value': True
            }
        )

    except Exception as e:
        print(f"Error enabling DNS support and hostnames: {e}")

vpc_id = None
if __name__ == "__main__":
    key_name=create_key_pair()
    public_ip = get_public_ip()
    dry_run = input("Dry run? (yes/no): ").strip().lower() == "yes"
    if public_ip:
        vpc_id, private_subnet_id, public_subnet_id, InternetGatewayId, public_route_table_id, private_route_table_id = create_vpc(key_name, public_ip)
        enable_dns_support_and_hostname(vpc_id)
        print(f"VPC ID: {vpc_id}")
        print(f"Private Subnet ID: {private_subnet_id}")
        print(f"Public Subnet ID: {public_subnet_id}")
        print(f"Internet Gateway ID: {InternetGatewayId}")
        print(f"Public Route Table ID: {public_route_table_id}")
        print(f"Private Route Table ID: {private_route_table_id}")
        print("Network Environemnt setup completed successfully")
    else:
        print("Failed to fetch public IP. Exiting script.")