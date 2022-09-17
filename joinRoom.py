# new user join: check if current rooms are full
# if not, find it and add this user to that room
# if all full, create a new room and add user to it
# join room with specific id is in another function

## !!!!! client request should be {"action": "joinRoom", "userId": 123}
#response body: {"action": "joinRoom", 'roomId': , 'position': ''}

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
    'action': 'joinRoom',
    'roomId': 0,
    'position': 'A',
}

maxRoomId=0

characterTiles='1W1, 1W2, 1W3, 1W4, 2W1,2W2,2W3,2W4,3W1,3W2,3W3,3W4,4W1,4W2,4W3,4W4,5W1,5W2,5W3,5W4,6W1,6W2,6W3,6W4,7W1,7W2,7W3,7W4,8W1,8W2,8W3,8W4,9W1,9W2,9W3,9W4'
dotTiles='1B1, 1B2, 1B3, 1B4, 2B1,2B2,2B3,2B4,3B1,3B2,3B3,3B4,4B1,4B2,4B3,4B4,5B1,5B2,5B3,5B4,6B1,6B2,6B3,6B4,7B1,7B2,7B3,7B4,8B1,8B2,8B3,8B4,9B1,9B2,9B3,9B4'
bambooTiles='1T1, 1T2, 1T3, 1T4, 2T1,2T2,2T3,2T4,3T1,3T2,3T3,3T4,4T1,4T2,4T3,4T4,5T1,5T2,5T3,5T4,6T1,6T2,6T3,6T4,7T1,7T2,7T3,7T4,8T1,8T2,8T3,8T4,9T1,9T2,9T3,9T4'


def lambda_handler(event, context):
    request_body=None
    userId=None
    connectionId=None
    room_list =None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        userId=int(request_body['userId'])
        
        # get metadata
        maxRoomId=metaTable.scan().get('Items', [])[0]['maxRoomId']
    
        #get unfull room
        scan_kwargs = {
            'FilterExpression': Key('usersCount').between(0,3) & Key('id').between(0,9999)
        }
        room_list = roomTable.scan(**scan_kwargs).get('Items', [])
        if len(room_list)!=0:
            body['roomId']=room_list[0]['id']
            if room_list[0]['usersCount']==0:
                body['position']='A'
                update_room_table(room_list[0]['id'], userId, 'A')
            elif room_list[0]['usersCount']==1:
                body['position']='B'
                update_room_table(room_list[0]['id'], userId, 'B')
            elif room_list[0]['usersCount']==2:
                body['position']='C'
                update_room_table(room_list[0]['id'], userId, 'C')
            elif room_list[0]['usersCount']==3:
                body['position']='D'
                update_room_table(room_list[0]['id'], userId, 'D')
            # response['body']=body
        else: #create a new room
            create_room(userId)
            update_metaTable()
            body['roomId']=maxRoomId+1
            body['position']='A'
        update_clientsTable(connectionId, body['roomId'])
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
    
def create_room(userId):
    #publicTiles: the tiles has played by u
    roomTable.put_item(
       Item={
            'id': maxRoomId+1,
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
    
def update_metaTable():
    metaTable.update_item(
        Key={
            'id': 0
        },
        UpdateExpression="set maxRoomId = maxRoomId + :val",
        ExpressionAttributeValues={
            ':val': 1
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