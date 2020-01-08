#!/usr/bin/env python
# AWS DISCLAMER
# ---

# The following files are provided by AWS Professional Services describe the process to create a IAM Policy with description.

# These are non-production ready and are to be used for testing purposes.

# These files is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. See the License
# for the specific language governing permissions and limitations under the License.

# (c) 2019 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
# http://aws.amazon.com/agreement or other written agreement between Customer and Amazon Web Services, Inc.​
import json
import os
import pytest
from inventory.mappers import EC2DataMapper

@pytest.fixture()
def full_ec2_config():
    with open(os.path.join(os.path.dirname(__file__), "sample_config_query_results/sample_ec2.json")) as file_data:
        file_contents = file_data.read()
        
    return json.loads(file_contents)

def test_given_resource_type_is_not_ec2_then_empty_array_is_returned(full_ec2_config):
    full_ec2_config["resourceType"] = "NOT EC2"

    mapper = EC2DataMapper()

    assert mapper.map(full_ec2_config) == []

def test_given_isntance_has_no_public_dns_ec2_then_dns_private_dns_is_used(full_ec2_config):
    del(full_ec2_config["configuration"]["publicDnsName"])
    del(full_ec2_config["configuration"]["networkInterfaces"][0]["privateIpAddresses"][0]["association"])

    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)

    assert len(mapped_result) == 1, "One row was expected"
    assert mapped_result[0].dns_name == full_ec2_config["configuration"]["privateDnsName"], "Private DNS should be used if public DNS is not available"

def test_given_isntance_has_blank_public_dns_ec2_then_dns_private_dns_is_used(full_ec2_config):
    full_ec2_config["configuration"]["publicDnsName"] = ""
    del(full_ec2_config["configuration"]["networkInterfaces"][0]["privateIpAddresses"][0]["association"])

    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)

    assert len(mapped_result) == 1, "One row was expected"
    assert mapped_result[0].dns_name == full_ec2_config["configuration"]["privateDnsName"], "Private DNS should be used if public DNS is not available"

def test_given_isntance_has_with_public_dns_ec2_then_dns_public_dns_is_used(full_ec2_config):
    full_ec2_config["configuration"]["publicDnsName"] = "example.com"

    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)

    assert len(mapped_result) == 2, "Two rows was expected since it is a public EC2 instance"
    assert mapped_result[0].dns_name == full_ec2_config["configuration"]["publicDnsName"], "Public DNS should be used if public DNS is available"

def test_given_ec2_instance_with_no_public_ip_then_one_item_returned(full_ec2_config):
    del(full_ec2_config["configuration"]["networkInterfaces"][0]["privateIpAddresses"][0]["association"])

    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)
    
    assert len(mapped_result) == 1, "One row was expected since instance only has one private IP"
    assert mapped_result[0].ip_address == full_ec2_config["configuration"]["networkInterfaces"][0]["privateIpAddresses"][0]["privateIpAddress"], "IP Address should match what was returned from config"

def test_given_ec2_instance_with_public_ip_then_two_items_returned(full_ec2_config):
    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)
    
    assert len(mapped_result) == 2, "Two rows were expected. One for the public IP and one for the private IP"
    assert mapped_result[1].ip_address == full_ec2_config["configuration"]["networkInterfaces"][0]["privateIpAddresses"][0]["association"]["publicIp"], "IP Address should match public IP returned from config"

def test_given_ec2_instance_with_public_dns_name_then_asset_is_marked_as_public(full_ec2_config):
    mapper = EC2DataMapper()

    mapped_result = mapper.map(full_ec2_config)
    
    assert len(mapped_result) == 2, "Two rows were expected. One for the public IP and one for the private IP"
    assert mapped_result[0].is_public == "Yes", "Instance should have been marked public since it has a public DNS name"
    assert mapped_result[1].is_public == "Yes", "Instance should have been marked public since it has a public DNS name"
