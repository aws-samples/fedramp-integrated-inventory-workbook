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
from botocore.exceptions import ClientError
from callee import String, Contains
import json
import os
from unittest.mock import MagicMock, Mock, patch, ANY
import pytest
from inventory.mappers import DataMapper
import inventory.readers
from inventory.readers import AwsConfigInventoryReader

def setup_function():
    os.environ["ACCOUNT_LIST"] = '[ { "name": "foo", "id": "210987654321"} ]'
    os.environ["CROSS_ACCOUNT_ROLE_NAME"] = "foobar"

def test_given_valid_arn_then_aws_partition_determined():
    mock_lambda_context = Mock()
    mock_lambda_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:testing"

    reader = AwsConfigInventoryReader(lambda_context=mock_lambda_context)

    aws_partition = reader._get_aws_partition()

    assert aws_partition == "aws", "Partition of ARN in context is aws"

@patch("inventory.readers._logger", autospec=True)
def test_given_unsupported_resource_type_then_warning_is_logged(mock_logger):
    mock_mapper = Mock(spec=DataMapper)
    mock_mapper.can_map.return_value = False
    mock_config_client_factory = Mock()
    mock_config_client_factory.return_value \
                              .select_resource_config \
                              .return_value = { "NextToken": None,
                                                "Results": [ json.dumps({ "resourceType": "foobar" }) ] }

    reader = AwsConfigInventoryReader(lambda_context=MagicMock(), sts_client=Mock(), mappers=[mock_mapper])
    reader._get_config_client = mock_config_client_factory

    all_inventory = reader.get_resources_from_all_accounts()

    assert len(all_inventory) == 0, "no inventory should be returned since there was nothing to map"
    mock_logger.warning.assert_called_with(String() & Contains("skipping mapping"))

@patch("inventory.readers._logger", autospec=True)
def test_given_error_from_boto_then_account_is_skipped_but_others_still_processed(mock_logger):
    os.environ["ACCOUNT_LIST"] = '[ { "name": "foo", "id": "210987654321" }, { "name": "bar", "id": "123456789012" } ]'
    mock_mapper = Mock(spec=DataMapper)
    mock_mapper.can_map.return_value = True
    mock_mapper.map.return_value = [ { "test": True }]
    mock_select_resource_config = Mock(side_effect=[ ClientError(error_response={'Error': {'Code': 'ResourceInUseException'}}, operation_name="select_resource_config"),
                                                    { "NextToken": None,
                                                      "Results": [ json.dumps({ "resourceType": "foobar" }) ] }])
    mock_config_client_factory = Mock()
    mock_config_client_factory.return_value \
                              .select_resource_config = mock_select_resource_config

    reader = AwsConfigInventoryReader(lambda_context=MagicMock(), sts_client=Mock(), mappers=[mock_mapper])
    reader._get_config_client = mock_config_client_factory
    
    all_inventory = reader.get_resources_from_all_accounts()

    assert len(all_inventory) == 1, "inventory from the successful call should be returned"
    assert len(mock_select_resource_config.mock_calls) == 2, "boto should have been called twice to page through results"
    mock_logger.error.assert_called_with(String() & Contains("moving onto next account"), ANY, ANY, exc_info=True)

def test_given_multiple_resource_pages_from_boto_then_reader_loops_through_all_pages():
    mock_mapper = Mock(spec=DataMapper)
    mock_mapper.can_map.return_value = False
    mock_select_resource_config = Mock(side_effect=[{ "NextToken": "nextpage",
                                                      "Results": [ json.dumps({ "resourceType": "foobar" }) ] },
                                                    { "NextToken": None,
                                                      "Results": [ json.dumps({ "resourceType": "foobar" }) ] }])
    mock_config_client_factory = Mock()
    mock_config_client_factory.return_value \
                              .select_resource_config = mock_select_resource_config

    readerx = AwsConfigInventoryReader(lambda_context=MagicMock(), sts_client=Mock(), mappers=[mock_mapper])
    readerx._get_config_client = mock_config_client_factory

    all_inventory = readerx.get_resources_from_all_accounts()

    assert len(all_inventory) == 0, "no inventory should be returned since there was nothing to map"
    assert len(mock_select_resource_config.mock_calls) == 2, "boto should have been called twice to page through results"
    assert mock_select_resource_config.call_args.kwargs["NextToken"] == "nextpage", "NextToken must use value from previous select_resource_config call"
