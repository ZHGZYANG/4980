# on connect: add client to clients table and return connectionId

import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

clientsTable=boto3.resource('dynamodb').Table('clients')
apigw = boto3.client('apigatewaymanagementapi')

response = {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
}

def lambda_handler(event, context):
    try:
        connectionId = event['requestContext']['connectionId']
        update_clientsTable(connectionId)
        response['statusCode']= 200
    except:
        response['statusCode']= 400
    return response

def update_clientsTable(connectionId):
    clientsTable.put_item(
      Item={
            'id': connectionId,
            'roomId': 0,
            'userId': 0,
        }
    )
