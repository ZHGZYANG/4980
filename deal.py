# deal (fa pai)
# only one user send this request (e.g. only user with position=A send)
# then server will forward result to other users

## !!!!! client request should be {"action": "deal", "roomId": 123}
#response body: {"action": "deal", 'roomId': 0, 'userId': 0, 'tiles': ''}

import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import random

testTable = boto3.resource('dynamodb').Table('test')
roomTable = boto3.resource('dynamodb').Table('room')
clientsTable=boto3.resource('dynamodb').Table('clients')
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
    'action': 'deal',
    'roomId': 0,
    'userId': 0,
    'tiles': '',
}

maxRoomId=0

characterTiles=['1W1', '1W2', '1W3', '1W4', '2W1', '2W2', '2W3', '2W4', '3W1', '3W2', '3W3', '3W4', '4W1', '4W2', '4W3', '4W4', '5W1', '5W2', '5W3', '5W4', '6W1', '6W2', '6W3', '6W4', '7W1', '7W2', '7W3', '7W4', '8W1', '8W2', '8W3', '8W4', '9W1', '9W2', '9W3', '9W4']
dotTiles=['1B1', '1B2', '1B3', '1B4', '2B1', '2B2', '2B3', '2B4', '3B1', '3B2', '3B3', '3B4', '4B1', '4B2', '4B3', '4B4', '5B1', '5B2', '5B3', '5B4', '6B1', '6B2', '6B3', '6B4', '7B1', '7B2', '7B3', '7B4', '8B1', '8B2', '8B3', '8B4', '9B1', '9B2', '9B3', '9B4']
bambooTiles=['1T1', '1T2', '1T3', '1T4', '2T1', '2T2', '2T3', '2T4', '3T1', '3T2', '3T3', '3T4', '4T1', '4T2', '4T3', '4T4', '5T1', '5T2', '5T3', '5T4', '6T1', '6T2', '6T3', '6T4', '7T1', '7T2', '7T3', '7T4', '8T1', '8T2', '8T3', '8T4', '9T1', '9T2', '9T3', '9T4']
allTiles=characterTiles+dotTiles+bambooTiles

def lambda_handler(event, context):
    connectionId=None
    roomId=None
    request_body=None
    tilesList=[]
    tileForBanker=''
    bankerUserId=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        
        body['roomId']=roomId
        #get specific room
        room = roomTable.get_item(Key={'id': roomId})
        if room['publicTiles']=='':
            random.shuffle(allTiles)
            tilesList.append(allTiles[0:14])
            tilesList.append(allTiles[15:29])
            tilesList.append(allTiles[29:42])
            tilesList.append(allTiles[42:55])
            reminingTiles=allTiles[55:]
            tileForBanker=allTiles[14]
            
            banker=room['banker']
            if banker=='A':
                bankerUserId=room['userIDA']
                tilesList[0].append(tileForBanker)
            elif banker=='B':
                bankerUserId=room['userIDB']
                tilesList[1].append(tileForBanker)
            elif banker=='C':
                bankerUserId=room['userIDC']
                tilesList[2].append(tileForBanker)
            else:
                bankerUserId=room['userIDD']
                tilesList[3].append(tileForBanker)
    
            update_room_table(roomId, tilesList, reminingTiles)
            
            #forward to all users in this room
            userIDList=[]
            userIDList.append(room['userIDA'])
            userIDList.append(room['userIDB'])
            userIDList.append(room['userIDC'])
            userIDList.append(room['userIDD'])
            for i in range(4):
                body['userId']=userIDList[i]
                body['tiles']=','.join(tilesList[i])
                scan_kwargs = {'FilterExpression': Key('userId').eq(userIDList[i])
                connId = clientsTable.scan(**scan_kwargs).get('Items', [])[0]['id']
                apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connId)
        else:
            res={'message': 'opration not allowed! The game has started!'}
            apigw.post_to_connection(Data=bytes(str(res), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, tilesList, reminingTiles):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set userACurrentTiles = :userACurrentTiles, userBCurrentTiles = :userBCurrentTiles, userCCurrentTiles = :userCCurrentTiles, userDCurrentTiles = :userDCurrentTiles, reminingTiles = :reminingTiles",
        ExpressionAttributeValues={
            'reminingTiles': ','.join(reminingTiles),
            ':userACurrentTiles': ','.join(tilesList[0]),
            ':userBCurrentTiles': ','.join(tilesList[1]),
            ':userCCurrentTiles': ','.join(tilesList[2]),
            ':userDCurrentTiles': ','.join(tilesList[3])
        }
    )