# draw (mo pai)

## !!!!! client request should be {"action": "draw", "roomId": 123, "userId": 123, "position": "A", "count": 1}
#response body: {"action": "draw", 'roomId': 123, 'newTile': '2T2'}

import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

testTable = boto3.resource('dynamodb').Table('test')
userTable = boto3.resource('dynamodb').Table('users')
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
    "action": "draw",
    'roomId': 0,
    'newTile': ''
}



def lambda_handler(event, context):
    connectionId=None
    roomId=None
    userId=None
    request_body=None
    position=None
    count=0
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        userId=int(request_body['userId'])
        position=request_body['position']
        count=int(request_body['count'])
        body['roomId']=roomId
        #get specific room
        room = roomTable.get_item(Key={'id': roomId})
        if count==1:
            reminingTiles=room['reminingTiles'].split(',')
            newTile=reminingTiles.pop()
            userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
            userCurrentTiles.append(newTile)
            body['newTile']=newTile
            update_room_table(roomId, reminingTiles, userCurrentTiles, position)
            apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        else:
            res={'message': 'Count in request body is not 1: THIS IS JUST TESTING'}
            apigw.post_to_connection(Data=bytes(str(res), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, reminingTiles, userCurrentTiles, position):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set user"+position+"CurrentTiles = :userCurrentTiles, reminingTiles = :reminingTiles",
        ExpressionAttributeValues={
            'reminingTiles': ','.join(reminingTiles),
            ':userCurrentTiles': ','.join(userCurrentTiles),

        }
    )