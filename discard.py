# discard(da pai)

## !!!!! client request should be {"action": "discard", "roomId": 123, "userId": 123, "position": "A", "tile": "1W1"}
#response body to requester: {"action": "discard", 'roomId': 123, 'publicTiles': '1W1,2W2,3W3,4W4'}

#response body to other users: {"action": "discardFromOthers", 'roomId': 123, "actionUserId": 123, "actionuserPosition": "A", 'discardedTile': '1W1', 'publicTiles': '1W1,2W2,3W3,4W4'}
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
    'action': 'discard',
    'roomId': 0,
    'publicTiles': ''
}

bodyOthers={
    'action': 'discardFromOthers',
    'roomId': 0,
    'actionUserId': 0,
    'actionuserPosition': '', 
    'discardedTile': '',
    'publicTiles': ''
}


def lambda_handler(event, context):
    connectionId=None
    roomId=None
    userId=None
    position=None
    tile=None
    request_body=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        userId=int(request_body['userId'])
        position=request_body['position']
        tile=request_body['tile']
        
        bodyRequester['roomId']=roomId
        bodyOthers['roomId']=roomId
        bodyOthers['actionUserId']=userId
        bodyOthers['actionuserPosition']=position
        bodyOthers['discardedTile']=tile
        
        #get specific room
        room = roomTable.get_item(Key={'id': roomId})
        publicTiles=room['publicTiles'].split(',')
        userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
        publicTiles.append(tile)
        userCurrentTiles.remove(tile)
        
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