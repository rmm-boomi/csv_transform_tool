import re
import json
import csv_tools

VALID_API_KEY="a-made-up-secret-value-123456"

def post__run_opertions(params, body):
    operations = json.loads(body)
    filename = params[0]
    print(f"LOG: Run Operations request received:\n{operations}")
    running_value = csv_tools.run_operations(filename, operations)

    if running_value['type'] == 'csv':
        response_body = running_value['data'].to_csv(index=False)
        response_type = 'text/csv'
    elif running_value['type'] == 'json':
        response_body = running_value['data']
        response_type = 'application/json'
    else:
        response_body = running_value['data']
        response_type = 'text/plain'

    return {'status': 200, 'body': response_body, 'contentType': response_type}

def lambda_handler(event, context):
    # Check headers for valid API key
    normalized_headers = {key.lower(): value for key, value in event['headers'].items()}
    authHeader = normalized_headers['authorization']
    if authHeader is None or authHeader != f'Bearer {VALID_API_KEY}':
        return {
            'statusCode': 401,
            'body': 'Invalid API key'
        }

    # Get path and params
    req_path = event['requestContext']['http']['path']
    path_match = re.match(r"^/file/([^/]*)/run-operations$", req_path)
    if path_match is None:
        return {
            'statusCode': 404,
            'body': 'Route not found'
        }
    path_params = list(path_match.groups())
    print(f"LOG: Request received: {req_path}")

    # Get request body - convert to string if not already (local dev will be a dict)
    req_body = event.get('body', None)
    if not isinstance(req_body, str):
        req_body = json.dumps(req_body)
    
    # Run the handler
    response = post__run_opertions(path_params, req_body)
    
    # Return the response
    return {
        'statusCode': response['status'],
        'headers': {
            'Content-Type': response['contentType']
        },
        'body': response['body']
    }