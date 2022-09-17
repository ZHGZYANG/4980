# history

# request body: {"action": "history", "userId": 123}

# response body: {"action": "history", "userId": 123, "lostCount": 1, "ranking": 1, "username": "abcd", "winCount": 1}


import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

testTable = boto3.resource('dynamodb').Table('test')
userTable = boto3.resource('dynamodb').Table('users')
clientsTable=boto3.resource('dynamodb').Table('clients')
metaTable=boto3.resource('dynamodb').Table('metadata')
apigw = boto3.client('apigatewaymanagementapi',
endpoint_url='https://6upodzvebj.execute-api.us-east-1.amazonaws.com/production/')

response = {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
}


body={
    'action': 'history',
    'userId': 2,
    "lostCount": 1, 
    "ranking": 1, 
    "username": "abcd", 
    "winCount": 1
}

def lambda_handler(event, context):
    # write_test_table(str(event))
    # return response
    request_body=None
    username=None
    connectionId=None
    
    request_body=json.loads(event['body'])
    userId=request_body['userId']
    connectionId = event['requestContext']['connectionId']
    
    currentUser=userTable.get_item(Key={'id': userId})
    body['userId']=userId
    body['lostCount']=currentUser['lostCount']
    body['ranking']=currentUser['ranking']
    body['username']=currentUser['username']
    body['winCount']=currentUser['winCount']
    apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
    return response
    
