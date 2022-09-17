# AI Action: discard(da pai), draw(mo pai), pongKong, meld

# client request should be {"action": "AIPlayerAction", "roomId": 123, "AIPosition": "A"}
# this request should be sent by the previous user (e.g. AI player position is A, user with position D should send this request)
#response to other users: SAME AS SINGLE REQUEST FOR DISCARD, DRAW, PONGKONG, MELD
# this function has no direct response to the requester

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
    'action': 'discardFromOthers',
    'roomId': 0,
    'actionUserId': 99999,
    'actionuserPosition': '', 
    'discardedTile': '',
    'publicTiles': ''
}
meldBody={
    'action': 'meld',
    'roomId': 0,
    'userId': 99999,
    'position': '',
}


def lambda_handler(event, context):
    roomId=None
    request_body=None
    
    try:
        request_body=json.loads(event['body'])
        roomId=int(request_body['roomId'])
        position=request_body['AIPosition']
        
        if meld(roomId, position):
            meldBody['roomId']=roomId
            meldBody['position']=position
            userIDList=[]
            for p in ['A', 'B', 'C', 'D']:
                if p!=position:
                    userIDList.append(room['userID'+p])
            for i in range(3):
                scan_kwargs = {'FilterExpression': Key('userId').eq(userIDList[i])
                connId = clientsTable.scan(**scan_kwargs).get('Items', [])[0]['id']
                apigw.post_to_connection(Data=bytes(str(meldBody), encoding='utf-8'), ConnectionId=connId)
            return response
            
        #discard a tile
        correlation={'1':[], '2':[],'3':[],'4':[],'5':[]}
        room = roomTable.get_item(Key={'id': roomId})
        userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
        userCurrentTiles_=[tile[:2] for tile in userCurrentTiles]

        for t in ['W','B','T']:
            for i in range(1,10):
                count=userCurrentTiles_.count(str(i)+t)
                if count>2:
                    for k in userCurrentTiles:
                        if k[:2]==str(i)+t:
                            correlation['5'].append(k)
                elif count==2:
                    for k in userCurrentTiles:
                        if k[:2]==str(i)+t:
                            correlation['3'].append(k)
                elif count==1:
                    for k in userCurrentTiles:
                        if k[:2]==str(i)+t:
                            correlation['1'].append(k)

        tile=''
        for i in range(1,6):
            if len(correlation[str(i)])!=0:
                tile=correlation[str(i)].pop()
                break
        
        body['roomId']=roomId
        body['actionuserPosition']=position
        body['discardedTile']=tile
        
        #get specific room
        publicTiles=room['publicTiles'].split(',')
        userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
        publicTiles.append(tile)
        userCurrentTiles.remove(tile)
        
        update_room_table_discard(roomId, publicTiles, userCurrentTiles, position)

        body['publicTiles']=','.join(publicTiles)
        
        sendMessages(position, room)
        
        draw(roomId, position)
        
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
        
def sendMessages(position, room):
    #forward to all users in this room
    userIDList=[]
    for p in ['A', 'B', 'C', 'D']:
        if p!=position:
            userIDList.append(room['userID'+p])
    for i in range(3):
        scan_kwargs = {'FilterExpression': Key('userId').eq(userIDList[i])
        connId = clientsTable.scan(**scan_kwargs).get('Items', [])[0]['id']
        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connId)

   
def pongKong(roomId, publicTiles, userCurrentTiles, position):
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

def draw(roomId, position):
    room = roomTable.get_item(Key={'id': roomId})
    reminingTiles=room['reminingTiles'].split(',')
    newTile=reminingTiles.pop()
    userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
    userCurrentTiles.append(newTile)
    update_room_table_draw(roomId, reminingTiles, userCurrentTiles, position)
    
def meld(roomId, position):
    room = roomTable.get_item(Key={'id': roomId})
    userCurrentTiles=room['user'+position+'CurrentTiles'].split(',')
    userCurrentTiles=[tile[:2] for tile in userCurrentTiles]
    total_count=len(userCurrentTiles)
    counterTable = {}
    for i in userCurrentTiles:
        counterTable[i] = userCurrentTiles.count(i)
    count_abc=0
    count_aaa=0
    count_dd=0
    middle_abc_list=[]
    for item in counterTable:
        if counterTable[item]==2:
            count_dd+=1
        elif counterTable[item]==3:
            count_aaa+=1
        elif counterTable[item]==4:
            middle_abc_list.append(item)
    if count_dd==1:
        for item in middle_abc_list:
            if str(int(item[:1])-1)+item[1:2] not in counterTable and str(int(item[:1])+1)+item[1:2] not in counterTable:
                return 0
        return 1
    else:
        return 0
   
def update_room_table_draw(roomId, reminingTiles, userCurrentTiles, position):
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
    
def update_room_table_discard(roomId, publicTiles, userCurrentTiles, position):
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