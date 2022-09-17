# logout

import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

clientsTable=boto3.resource('dynamodb').Table('clients')

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
    
        clientsTable.update_item(
            Key={
                'id': connectionId
            },
            UpdateExpression="set userId = :val",
            ExpressionAttributeValues={
                ':val': -1
            }
        )
    
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
 