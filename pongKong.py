# Pong & Kong (take a tile from publicTiles and forward msg to others)

## !!!!! client request should be {"action": "pongKong", "userId": 123, "position": "A", "type": "pong", "tileFromPublic": "1W1"}
#response body to requester: {"action": "pongKong", 'roomId': 123, 'publicTiles': '1W1,2W2,3W3,4W4'}

# response body to other users: {"action": "pongKongReceive", 'roomId': 123, 'type': 'pong', 'publicTiles': '1W1,2W2,3W3,4W4', "pongedTile": "1W1"}

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

bodyRequester={
    'action': 'pongKong',
    'roomId': 0,
    'publicTiles': ''
}

bodyOthers={
    'action': 'pongKongReceive',
    'roomId': 0,
    'actionUserId': 0,
    'actionuserPosition': '', 
    'type': '',
    'publicTiles': '',
    'pongedTile': ''
}



def lambda_handler(event, context):
    connectionId=None
    roomId=None
    userId=None
    position=None
    tileFromPublic=None
    type=None
    request_body=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        userId=int(request_body['userId'])
        position=request_body['position']
        tileFromPublic=request_body['tileFromPublic']
        type=request_body['type']
        
        bodyRequester['roomId']=roomId
        bodyOthers['roomId']=roomId
        bodyOthers['actionUserId']=userId
        bodyOthers['actionuserPosition']=position
        bodyOthers['pongedTile']=tileFromPublic
        bodyOthers['type']=type
        
        #get specific room
        room = roomTable.get_item(Key={'id': roomId})
        publicTiles=room['publicTiles'].split(',')
        userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
        publicTiles.remove(tileFromPublic)
        userCurrentTiles.append(tileFromPublic)
        
        update_room_table(roomId, publicTiles, userCurrentTiles, position)
        
        bodyRequester['publicTiles']=','.join(publicTiles)
        bodyOthers['publicTiles']=','.join(publicTiles)
        
        #forward to all users in this room
        apigw.post_to_connection(Data=bytes(str(bodyRequester), encoding='utf-8'), ConnectionId=connectionId)
        
        userIDList=[]
        for p in ['A', 'B', 'C', 'D']:
            if p!=position:
                userIDList.append(room['userID'+p])
        for i in range(3):
            scan_kwargs = {'FilterExpression': Key('userId').eq(userIDList[i])
            connId = clientsTable.scan(**scan_kwargs).get('Items', [])[0]['id']
            apigw.post_to_connection(Data=bytes(str(bodyOthers), encoding='utf-8'), ConnectionId=connId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, publicTiles, userCurrentTiles, position):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set user"+position+"CurrentTiles = :userCurrentTiles, publicTiles = :publicTiles",
        ExpressionAttributeValues={
            'publicTiles': ','.join(publicTiles),
            ':userCurrentTiles': ','.join(userCurrentTiles[0])
        }
    )