import json
import boto3

apigw = boto3.client('apigatewaymanagementapi',
endpoint_url='https://6upodzvebj.execute-api.us-east-1.amazonaws.com/production/')

response = {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
}

def lambda_handler(event, context):
    connectionId = event['requestContext']['connectionId']
    res=apigw.post_to_connection(Data=b'Server connected', ConnectionId=connectionId)
    return response
