# login

#responce body[JSON]:
#{
#    action: login
#    status  0:successful; 1: password does not match; 2: other error
#    userId  # have this entry only status=0
#    message 'Login successfully.'
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
    'action': 'login',
    'status': 2, # 0:successful; 1: password does not match; 2: no user
    'message': 'No user found.'
}

def lambda_handler(event, context):
    # write_test_table(str(event))
    # return response
    request_body=None
    username=None
    password=None
    connectionId=None
    user_list =None
    try:
        request_body=json.loads(event['body'])
        username=request_body['username']
        password=request_body['password']
        connectionId = event['requestContext']['connectionId']
        
        scan_kwargs = {
            'FilterExpression': Key('username').begins_with(username)
        }
        user_list = userTable.scan(**scan_kwargs).get('Items', [])
        if len(user_list)!=0:
            for user in user_list:
                if username==user['username']: # find user
                    if password==user['password']:
                        body['status']=0
                        body['userId']=user['id']
                        body['message']='Login successfully.'
                    else: # pswd wrong
                        body['status']=1
                        body['message']='Password does not match.'
                    break
        if body['status']==0:
            update_clientsTable(body['userId'], connectionId)
        apigw.post_to_connection(Data=bytes(str(body), encoding='utf-8'), ConnectionId=connectionId)
        return response
    except:
        return {'statusCode': 400,'headers': {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}}
    

def update_clientsTable(userId, connectionId):
    clientsTable.update_item(
        Key={'id': connectionId},
        UpdateExpression="set userId=:userId",
        ExpressionAttributeValues={':userId': userId},
    )

def update_userTable(userId):
    userTable.update_item(
        Key={'id': userId},
        UpdateExpression="set status=1"
    )
    
def write_test_table(data):
    testTable.put_item(
      Item={'id': data}
    )