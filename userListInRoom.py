# get all users userId in a room

## !!!!! client request should be {"action": "userListInRoom", "roomId": 123}
#response body: {"action": "userListInRoom", "roomId": 123, "positionA": 145, "positionB": "-", "positionC": "-", "positionD": "-"}

import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

roomTable = boto3.resource('dynamodb').Table('room')
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
    'action': 'userListInRoom',
    'roomId': 0,
    "positionA": "-", 
    "positionB": "-", 
    "positionC": "-", 
    "positionD": "-"
}


def lambda_handler(event, context):
    request_body=None
    connectionId=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        
        #get room
        room = roomTable.get_item(Key={'id': roomId})
        body['roomId']=roomId
        for p in ['A','B','C','D']:
            if room['userID'+p]!=0:
                body['position'+p]=room['userID'+p]

        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
