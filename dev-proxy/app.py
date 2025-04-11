import requests
from flask import Flask, request, Response

LOCAL_LAMBDA_HOST = '127.0.0.1:3001'
TARGET_URL = 'http://{}/2015-03-31/functions/{}/invocations'

app = Flask(__name__)

@app.route('/<function>', methods=['POST'])
def forward_request(function):
    url = TARGET_URL.format(LOCAL_LAMBDA_HOST, function)
    response = requests.post(url, headers=request.headers, data=request.data)
    response.raise_for_status()
    lambda_response = response.json()
    return Response(lambda_response['body'], status=lambda_response['statusCode'], headers=lambda_response['headers'])