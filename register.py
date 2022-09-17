# new user register

#responce body[JSON]:
#{
#    action: register
#    status  0:successful; 1: username exists; 2: other error
#    userId
#    message 'Account registered successfully.'
#}


import json
import boto3
from boto3.dynamodb.conditions import Key
import datetime

testTable = boto3.resource('dynamodb').Table('test')
userTable = boto3.resource('dynamodb').Table('users')
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
    'action': 'register',
    'status': 0, # 0:successful; 1: username exists; 2: other error
    'message': 'Account registered successfully.'
}

maxUserId=0

def lambda_handler(event, context):
    # write_test_table(str(event))
    # return response
    username=""
    password=""
    connectionId=""
    user_list=[]
    
    try:
        username=json.loads(event['body'])['username']
        password=json.loads(event['body'])['password']
        connectionId = event['requestContext']['connectionId']
        
        # get metadata
        global maxUserId;
        maxUserId=metaTable.scan().get('Items', [])[0]['maxUserId']
    
        #check if username exists
        scan_kwargs = {
            'FilterExpression': Key('username').begins_with(username)
        }
        user_list = userTable.scan(**scan_kwargs).get('Items', [])
        if len(user_list)!=0:
            for user in user_list:
                if username==user['username']: # username has been used
                    body['status']=1
                    body['user-input']=username
                    body['user-db']=user['username']
                    body['message']='Username has been used, please try another one.'
                    break
        if body['status']==0: # username can be used
            body['userId']=maxUserId+1
            create_user(username, password)
            update_metaTable()
        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}

def create_user(username, password):
    global maxUserId;
    userTable.put_item(
      Item={
            'id': maxUserId+1,
            'lostCount': 0,
            'password': password,
            'ranking': 0,
            'status': '',
            'username': username,
            'winCount': 0,
        }
    )
    
def update_metaTable():
    metaTable.update_item(
        Key={
            'id': 0
        },
        UpdateExpression="set maxUserId = maxUserId + :val",
        ExpressionAttributeValues={
            ':val': 1
        }
    )