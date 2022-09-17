# new user join with specific room number
# if not, find it and add this user to that room
# the roomId should be a 5-digit number

## !!!!! client request should be {"action": "joinRoomNumber", "userId": 123, "roomId": 123}
#response body: {"action": "joinRoomNumber", 'roomId': , 'position': ''}

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
    'action': 'joinRoomNumber',
    'roomId': 0,
    'position': 'A',
}

maxRoomId=0

def lambda_handler(event, context):
    request_body=None
    userId=None
    connectionId=None
    room_list =None
    roomId=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        userId=int(request_body['userId'])
        roomId=int(request_body['roomId'])
        
        scan_kwargs = {
            'FilterExpression': Key('id').eq(roomId)
        }
        room_list = roomTable.scan(**scan_kwargs).get('Items', [])
        body['roomId']=roomId
        if len(room_list)!=0:
            if room_list[0]['usersCount']==0:
                body['position']='A'
                update_room_table(roomId, userId, 'A')
            elif room_list[0]['usersCount']==1:
                body['position']='B'
                update_room_table(roomId, userId, 'B')
            elif room_list[0]['usersCount']==2:
                body['position']='C'
                update_room_table(roomId, userId, 'C')
            elif room_list[0]['usersCount']==3:
                body['position']='D'
                update_room_table(roomId, userId, 'D')
            else:
                body['roomId']=-1
                body['position']='Current room is full.'
        else: #create a new room
            create_room(userId, roomId)
        if body['roomId']!=-1:
            update_clientsTable(connectionId, roomId)
        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, userId, position):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set userID"+position+"=:userId, usersCount = usersCount + :val",
        ExpressionAttributeValues={
            ':userId': userId,
            ':val': 1
        }
    )
    
def create_room(userId, roomId):
    roomTable.put_item(
       Item={
            'id': roomId,
            'usersCount': 1,
            'endTime': '',
            'startTime': str(datetime.datetime.utcnow()),
            'userACurrentTiles': '',
            'userBCurrentTiles': '',
            'userCCurrentTiles': '',
            'userDCurrentTiles': '',
            'userAMeld': False,
            'userBMeld': False,
            'userCMeld': False,
            'userDMeld': False,
            'userAPoints': 0,
            'userBPoints': 0,
            'userCPoints': 0,
            'userDPoints': 0,
            'userIDA': userId,
            'userIDB': 0,
            'userIDC': 0,
            'userIDD': 0,
            'banker': '-',
            'publicTiles': '',
            'reminingTiles': '',
        }
    )
    
def update_clientsTable(connectionId, roomId):
    clientsTable.update_item(
        Key={
            'id': connectionId
        },
        UpdateExpression="set roomId = :val",
        ExpressionAttributeValues={
            ':val': roomId
        }
    )