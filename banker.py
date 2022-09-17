# assign banker(dealer)
# only one user send this request (e.g. only user with position=A send)
# then server will forward result to other users

## !!!!! client request should be {"action": "banker", "roomId": 123}
#response body: {"action": "banker", 'roomId': , 'banker': ''} banker: return position of the user

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
    'action': 'banker',
    'roomId': 0,
    'banker': 'A',
}

maxRoomId=0

characterTiles='1W1, 1W2, 1W3, 1W4, 2W1,2W2,2W3,2W4,3W1,3W2,3W3,3W4,4W1,4W2,4W3,4W4,5W1,5W2,5W3,5W4,6W1,6W2,6W3,6W4,7W1,7W2,7W3,7W4,8W1,8W2,8W3,8W4,9W1,9W2,9W3,9W4'
dotTiles='1B1, 1B2, 1B3, 1B4, 2B1,2B2,2B3,2B4,3B1,3B2,3B3,3B4,4B1,4B2,4B3,4B4,5B1,5B2,5B3,5B4,6B1,6B2,6B3,6B4,7B1,7B2,7B3,7B4,8B1,8B2,8B3,8B4,9B1,9B2,9B3,9B4'
bambooTiles='1T1, 1T2, 1T3, 1T4, 2T1,2T2,2T3,2T4,3T1,3T2,3T3,3T4,4T1,4T2,4T3,4T4,5T1,5T2,5T3,5T4,6T1,6T2,6T3,6T4,7T1,7T2,7T3,7T4,8T1,8T2,8T3,8T4,9T1,9T2,9T3,9T4'


def lambda_handler(event, context):
    connectionId=None
    roomId=None
    request_body=None
    
    try:
        connectionId = event['requestContext']['connectionId']
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        
    
        body['roomId']=roomId
        #get specific room
        room = roomTable.get_item(Key={'id': roomId})
        if room['banker']=='-': # banker not assigned yet
            banker='A'
            banker_random=random.randint(1,4)
            if banker_random==1:
                banker='A'
            elif banker_random==2:
                banker='B'
            elif banker_random==3:
                banker='C'
            else:
                banker='D'
            body['banker']=banker
            update_room_table(roomId, banker)
            
            #forward to all users in this room
            userIDList=[]
            userIDList.append(room['userIDA'])
            userIDList.append(room['userIDB'])
            userIDList.append(room['userIDC'])
            userIDList.append(room['userIDD'])
            for userID in userIDList:
                scan_kwargs = {'FilterExpression': Key('userId').eq(userID)
                connId = clientsTable.scan(**scan_kwargs).get('Items', [])[0]['id']
                apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connId)
        else:
            body['banker']=room['banker']
            apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    
def update_room_table(roomId, banker):
    roomTable.update_item(
        Key={
            'id': roomId
        },
        UpdateExpression="set banker = :banker",
        ExpressionAttributeValues={
            ':banker': banker
        }
    )