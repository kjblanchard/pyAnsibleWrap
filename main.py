import logging
import boto3
from botocore.exceptions import ClientError
from operator import attrgetter

import json

AWS_REGION = 'us-east-2'

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

vpc_client = boto3.client("ec2", region_name=AWS_REGION)


def describe_vpcs(tag, tag_values, max_items):
    try:
        paginator = vpc_client.get_paginator('describe_vpcs')
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],
            PaginationConfig={'MaxItems': max_items})
        full_result = response_iterator.build_full_result()
        vpc_list = []
        for page in full_result['Vpcs']:
            vpc_list.append(page)
    except ClientError:
        logger.exception('Could not describe vpcs')
        raise
    else:
        return vpc_list

def describe_sgs(tag, tag_values, max_items):
    try:
        paginator = vpc_client.get_paginator('describe_security_groups')
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],
            PaginationConfig={'MaxItems': max_items})
        full_result = response_iterator.build_full_result()
        security_groups_list = []
        for page in full_result['SecurityGroups']:
            security_groups_list.append(page)
    except ClientError:
        logger.exception('Could not describe vpcs')
        raise
    else:
        return security_groups_list

def get_updated_amis():
    AWS_REGION = "us-east-2"
    EC2_RESOURCE = boto3.resource('ec2', region_name=AWS_REGION)
    images = EC2_RESOURCE.images.filter(
        Filters=[
            {
                'Name': 'name',
                'Values': ['*ubuntu-bionic-18.04-amd64-server-*']
            },
            {
                'Name': 'architecture',
                'Values': ['x86_64']
            },
            {
                'Name': 'virtualization-type',
                'Values': ['hvm']
            },
            {
                'Name': 'root-device-type',
                'Values': ['ebs']
            }
        ],
        Owners=['099720109477']
    )

    image_details = sorted(list(images), key=attrgetter('creation_date'), reverse=True)
    print(image_details[0])




if __name__ == '__main__':
    TAG = 'region'
    TAG_VALUES = ['us-east-2']
    MAX_ITEMS = 10
    vpcs = describe_vpcs(TAG, TAG_VALUES, MAX_ITEMS)
    vpc_id = json.dumps(vpcs[0].get('VpcId')).replace('"', '')
    logger.info(vpc_id)
    TAG = 'Name'
    TAG_VALUES = ['SSH']
    security_group = describe_sgs(TAG, TAG_VALUES, MAX_ITEMS)
    sg_id = json.dumps(security_group[0].get('GroupId')).replace('"', '')
    logger.info(sg_id)
    logger.info(get_updated_amis())