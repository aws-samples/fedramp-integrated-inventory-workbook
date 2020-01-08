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
import os
from unittest.mock import Mock, mock_open, patch, ANY
from callee import String, Contains
import pytest
import inventory.reports
from inventory.reports import CreateReportCommandHandler, DeliverReportCommandHandler

@patch('inventory.reports.load_workbook')
def test_given_empty_inventory_list_then_report_is_still_written(mock_load_workbook):
    report_handler = CreateReportCommandHandler()

    report_handler.execute([])

    mock_load_workbook.return_value.save.assert_called()

@patch('builtins.open')
@patch('inventory.reports.datetime')
def test_given_report_file_exists_then_delivery_to_s3_uses_correct_file_naming_convention(mock_datetime, mock_open):
    test_bucket_name = "bucket"
    os.environ["REPORT_TARGET_BUCKET_NAME"] = test_bucket_name
    os.environ["REPORT_TARGET_BUCKET_PATH"] = "test/path"
    mock_s3_client = Mock()

    report_handler = DeliverReportCommandHandler(s3_client=mock_s3_client)
    report_url = report_handler.execute("somereport")

    # Only verifying that we try to format the datetime correctly as that's the most import part of the report file name
    mock_datetime.now.return_value.strftime.assert_called_with("%Y-%m-%d-%H-%M-%S")
    mock_s3_client.put_object.assert_called_with(Key=ANY, Bucket=test_bucket_name, Body=ANY)
    assert report_url is not None and len(report_url) > 0, "report URL should be returned"