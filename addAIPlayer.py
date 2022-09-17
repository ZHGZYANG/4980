# add AI player with specific room number
# the roomId should be a 5-digit number

## !!!!! client request should be {"action": "addAIPlayer", "roomId": 123}
#response body: {"action": "addAIPlayer", "AIPosition": "A", "roomId": 123}

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
    'action': 'addAIPlayer',
    'roomId': 0,
    'AIPosition': 'A',
}

maxRoomId=0

def lambda_handler(event, context):
    request_body=None
    connectionId=None
    room_list =None
    roomId=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        
        scan_kwargs = {
            'FilterExpression': Key('id').eq(roomId)
        }
        room_list = roomTable.scan(**scan_kwargs).get('Items', [])
        body['roomId']=roomId
        if len(room_list)!=0:
            if room_list[0]['usersCount']==0:
                body['AIPosition']='A'
                update_room_table(roomId, 'A')
            elif room_list[0]['usersCount']==1:
                body['AIPosition']='B'
                update_room_table(roomId, 'B')
            elif room_list[0]['usersCount']==2:
                body['AIPosition']='C'
                update_room_table(roomId, 'C')
            elif room_list[0]['usersCount']==3:
                body['AIPosition']='D'
                update_room_table(roomId, 'D')
            else:
                body['roomId']=-1
                body['AIPosition']='Current room is full.'
        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, position):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set userID"+position+"=:userId, usersCount = usersCount + :val",
        ExpressionAttributeValues={
            ':userId': 99999,
            ':val': 1
        }
    )
