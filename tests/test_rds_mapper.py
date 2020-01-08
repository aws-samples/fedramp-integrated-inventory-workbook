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
from inventory.mappers import RdsDataMapper

@pytest.fixture()
def full_rds_db_instance_config():
    with open(os.path.join(os.path.dirname(__file__), "sample_config_query_results/sample_rds_db.json")) as file_data:
        file_contents = file_data.read()
        
    return json.loads(file_contents)

def test_given_fully_configured_rds_instance_then_base_attributes_are_mapped(full_rds_db_instance_config):
    mapper = RdsDataMapper()

    mapped_result = mapper.map(full_rds_db_instance_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].network_id == full_rds_db_instance_config['configuration']['dBSubnetGroup']['vpcId'], "NetworkId must be mapped if the VPC ID exists in the configuration"
    assert mapped_result[0].hardware_model == full_rds_db_instance_config['configuration']['dBInstanceClass']
    assert mapped_result[0].software_product_name == f"{full_rds_db_instance_config['configuration']['engine']}-{full_rds_db_instance_config['configuration']['engineVersion']}"

def test_given_rds_instance_marked_as_private_then_is_mapped_as_not_public(full_rds_db_instance_config):
    full_rds_db_instance_config["configuration"]["publiclyAccessible"] = False

    mapper = RdsDataMapper()

    mapped_result = mapper.map(full_rds_db_instance_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "No", "Instance must be marked as not public if publiclyAccessible is set to False"

def test_given_rds_instance_marked_as_public_then_is_mapped_as_public(full_rds_db_instance_config):
    full_rds_db_instance_config["configuration"]["publiclyAccessible"] = True

    mapper = RdsDataMapper()

    mapped_result = mapper.map(full_rds_db_instance_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "Yes", "Instance must be marked as public if publiclyAccessible is set to True"

def test_given_rds_instance_with_no_subnet_group_then_networkid_is_left_blank(full_rds_db_instance_config):
    del(full_rds_db_instance_config["configuration"]["dBSubnetGroup"])

    mapper = RdsDataMapper()

    mapped_result = mapper.map(full_rds_db_instance_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].network_id == "", "Instance must be marked as public if publiclyAccessible is set to True"
