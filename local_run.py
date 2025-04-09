import json

from csv_transform_tool.app import lambda_handler

with open("events/new.json") as f:
    event = json.load(f)

response = lambda_handler(event, None)

print(json.dumps(response, indent=2))
