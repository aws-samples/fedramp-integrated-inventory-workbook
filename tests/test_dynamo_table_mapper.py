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
from inventory.mappers import DynamoDbTableDataMapper

@pytest.fixture()
def full_dynamo_config():
    with open(os.path.join(os.path.dirname(__file__), "sample_config_query_results/sample_dynamo_table.json")) as file_data:
        file_contents = file_data.read()
        
    return json.loads(file_contents)

def test_given_dynamo_table_then_base_attributes_mapped(full_dynamo_config):
    mapper = DynamoDbTableDataMapper()

    mapped_result = mapper.map(full_dynamo_config)
    
    assert len(mapped_result) == 1, "Expected one row to be mapped"
    assert mapped_result[0].unique_id == full_dynamo_config["arn"], "ARN should be mapped to unique id"
