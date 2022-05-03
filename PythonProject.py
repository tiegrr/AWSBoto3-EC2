import boto3
import os
import time

# function to create key pair, repeats if name already taken up to 10 times
def create_key_pair(key_pair_input):
    ec2 = boto3.client('ec2')
    for attempt in range(10):
        try:
            key_pair = ec2.create_key_pair(KeyName=key_pair_input)
            private_key = key_pair['KeyMaterial']

            # writes SSH key to file set to [name of the keypair].pem
            with os.fdopen(os.open(key_pair_input + '.pem', os.O_WRONLY | os.O_CREAT, 0o400), 'w') as handle:
                handle.write(private_key)
        except Exception:
            print('Key pair already exists.')
            key_pair_input = input('Enter a new key pair name: ')
        else:
            global key_pair_name
            key_pair_name = key_pair_input
            break
    else:
        print('Too many failed attempts')

def create_security_group():
    ec2 = boto3.resource('ec2')
    security_group = ec2.create_security_group(
        Description = 'Allow inbound SSH traffic',
        GroupName = 'Allow-SSH',
        # VpcId = ' Put VpcId here ' ,
        TagSpecifications = [
            {
                'ResourceType': 'security-group',
                'Tags' :[
                    {
                        'Key': 'Name',
                        'Value': 'Allow-SSH'
                    }
                ]
            }
        ]
    )

    security_group.authorize_ingress(
        CidrIp='0.0.0.0/0',
        FromPort=22,
        ToPort=22,
        IpProtocol='tcp',
    )

    global security_id
    security_id = security_group.id
    
# function to create key pair, repeats if name already taken up to 10 times
def create_ec2_instance(ec2_input):
    ec2 = boto3.resource('ec2')
    for attempt in range(10):
        try:
            instances = ec2.create_instances(
                ImageId = 'ami-0c02fb55956c7d316',
                InstanceType = 't3.micro',
                MinCount = 1,
                MaxCount = 1,
                KeyName = key_pair_name,
                SecurityGroupIds = [security_id],
                TagSpecifications = [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': ec2_input
                            }
                        ]
                    }
                ]
            )

            for instance in instances:
                instance.wait_until_running()
                print(f'EC2 instance {ec2_input} has been launched with ID {instance.id}')
        except Exception:
            print('Instance already exists.')
            ec2_input = input('Enter a new instance name: ')
        else:
            break

        
            
    else:
        print('Too many failed attempts')

# asks for key pair name and runs create_key_pair function to create
key_pair_name = input('Enter key pair name: ')
create_key_pair(key_pair_name) 

# create SSH security group
create_security_group()

# create_ec2_instance
ec2_name = input('Enter EC2 instance name: ')
create_ec2_instance(ec2_name)