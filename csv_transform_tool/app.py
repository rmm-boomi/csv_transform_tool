import json

def lambda_handler(event, context):
    name = event['name'] if 'name' in event else "World"

    return {
        "statusCode": 200,
        "body": f"Hello {name}!",
    }
