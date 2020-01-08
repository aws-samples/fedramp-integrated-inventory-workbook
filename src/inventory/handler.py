# (c) 2019 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# License:
# This sample code is made available under the MIT-0 license. See the LICENSE file.
from inventory.readers import AwsConfigInventoryReader
from inventory.reports import CreateReportCommandHandler, DeliverReportCommandHandler

def lambda_handler(event, context):
    inventory = AwsConfigInventoryReader(lambda_context=context).get_resources_from_all_accounts()

    report_path = CreateReportCommandHandler().execute(inventory)
    report_url = DeliverReportCommandHandler().execute(report_path)

    return {'statusCode': 200,
            'body': {
                    'report': { 'url': report_url }
                }
            }

if __name__ == "__main__":
    class Context(object):
        def __init__(self):
            self.invoked_function_arn = "arn:aws-us-gov:lambda:us-east-1:123456789012:function:testing"

    result = lambda_handler(None, Context())

    print(result)
