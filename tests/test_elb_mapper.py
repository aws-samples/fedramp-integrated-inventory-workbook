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
from inventory.mappers import ElbDataMapper

@pytest.fixture()
def full_classic_elb_config():
    with open(os.path.join(os.path.dirname(__file__), "sample_config_query_results/sample_classic_elb.json")) as file_data:
        file_contents = file_data.read()
        
    return json.loads(file_contents)

def test_given_classic_elb_then_base_attributes_mapped(full_classic_elb_config):
    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_classic_elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].unique_id == full_classic_elb_config["arn"], "ARN should be mapped to unique id"
    assert mapped_result[0].network_id == full_classic_elb_config["configuration"]["vpcid"], "VPC ID should be mapped to network id"

def test_given_resource_type_is_not_classic_elb_then_empty_array_is_returned(full_classic_elb_config):
    full_classic_elb_config["resourceType"] = "NOT ELB"

    mapper = ElbDataMapper()

    assert mapper.map(full_classic_elb_config) == []

def test_given_internet_facing_classic_elb_then_it_is_mapped_as_public(full_classic_elb_config):
    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_classic_elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "Yes", "ELB should have been marked as public given internet facing scheme"

def test_given_internal_classic_elb_then_it_is_not_mapped_as_public(full_classic_elb_config):
    full_classic_elb_config["configuration"]["scheme"] = "internal"

    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_classic_elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "No", "ELB should have been marked as private"

_sample_v2elb_file_contents = None

@pytest.fixture
def full_v2elb_config():
    global _sample_v2elb_file_contents

    if not _sample_v2elb_file_contents:
        with open(os.path.join(os.path.dirname(__file__), "sample_config_query_results/sample_v2elb.json")) as file_data:
            _sample_v2elb_file_contents = file_data.read()
        
    return json.loads(_sample_v2elb_file_contents)

def test_given_v2elb_then_base_attributes_mapped(full_v2elb_config):
    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_v2elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].unique_id == full_v2elb_config["arn"], "ARN should be mapped to unique id"
    assert mapped_result[0].network_id == full_v2elb_config["configuration"]["vpcId"], "VPC ID should be mapped to network id"

def test_given_internet_facing_v2elb_then_it_is_mapped_as_public(full_v2elb_config):
    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_v2elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "Yes", "ELB should have been marked as public given internet facing scheme"

def test_given_internal_v2elb_then_it_is_not_mapped_as_public(full_v2elb_config):
    full_v2elb_config["configuration"]["scheme"] = "internal"

    mapper = ElbDataMapper()

    mapped_result = mapper.map(full_v2elb_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].is_public == "No", "ELB should have been marked as private"

