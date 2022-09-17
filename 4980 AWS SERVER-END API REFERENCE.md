# AWS Backend API Reference



WebSocket URL: wss://6upodzvebj.execute-api.us-east-1.amazonaws.com/production/



### 1. login

#### request body: 

{"action": "login", "username": "123", "password": "afesafr"}

#### response body: 

{"action": "login",  "status":  0, "userId": 123, "message": "Login successfully."}

#### Note:

status:  0:successful; 1: password does not match; 2: other error

userId:  have this entry only status=0



### 2. logout

#### request body:

{"action": "logout"}

#### response body: NO NEED



### 3. register

#### request body: 

{"action": "register", "username": "123", "password": "afesafr"}

#### response body: 

{"action": "register", "status":  0, "userId": 123, "message": "Account registered successfully."}

#### Note:

status:  0:successful; 1: username exists; 2: other error

userId:  have this entry only status=0



### 4. Join room

#### request body: 

{"action": "joinRoom", "userId": 123}

#### response body: 

{"action": "joinRoom", 'roomId': 123, 'position': 'A'}

#### Note:

position; A or B or C or D



### 5. Join room with room number

#### request body: 

{"action": "joinRoomNumber", "userId": 123, "roomId": 123}

#### response body: 

{"action": "joinRoomNumber", 'roomId': 123, 'position': 'A'}

#### Note:

position; A or B or C or D



### 6. assign banker 庄家（骰子 -server指定 传给CLIENT）

#### request body: 

{"action": "banker", "roomId": 123}

#### response body: 

{"action": "banker", 'roomId': 123, 'banker': 'A'} 

#### Note:

banker: return position of the user

开局后指定4人中一人发请求（例如只position=A的玩家请求），请求之后server会转发结果给所有user



### 7. Deal 发牌 （庄家14张手牌，闲家13张手牌 -server指定 传给CLIENT）

#### request body: 

{"action": "deal", "roomId": 123}

#### response body: 

{"action": "deal", 'roomId': 0, 'userId': 0, 'tiles': '1W1, 2W2, 3W3, 4W4'}

#### Note:

选好庄家后指定4人中一人发请求（例如只position=A的玩家请求），请求之后server会转发结果给所有user



### 8. draw 摸牌

#### request body: 

{"action": "draw", "roomId": 123, "userId": 123, "position": "A", "count": 1}

#### response body: 

{"action": "draw", 'roomId': 123, 'newTile': '2T2'}

#### Note:

count: 一般摸牌只需一张，所以需默认传1



### 9. discard 打一张牌

#### request body: 

{"action": "discard", "roomId": 123, "userId": 123, "position": "A", "tile": "1W1"}

#### response body to requester:

{"action": "discard", 'roomId': 123, 'publicTiles': '1W1,2W2,3W3,4W4'}

#### response body to other users:

{"action": "discardFromOthers", 'roomId': 123, "actionUserId": 123, "actionuserPosition": "A", 'discardedTile': '1W1', 'publicTiles': '1W1,2W2,3W3,4W4'}



### 10. Pong & Kong

#### request body: 

{"action": "pongKong", "roomId": 123, "userId": 123, "position": "A", "type": "pong", "tileFromPublic": "1W1"}

#### response body to requester:

{"action": "pongKong", 'roomId': 123, 'publicTiles': '1W1,2W2,3W3,4W4'}

#### response body to other users:

{"action": "pongKongReceive", 'roomId': 123, "actionUserId": 123, "actionuserPosition": "A", 'type': 'pong', 'publicTiles': '1W1,2W2,3W3,4W4', "pongedTile": "1W1"}

#### Note:

type: "pong" or "kong"  *This is CASE-SENSITIVE

tileFromPublic: the tile you will take in (discarded by others)

pongedTile: the tile requester used to take action pong or kong



### 11. Meld

#### request body: 

{"action": "meld", "roomId": 123, "userId": 123, "position": "A"}

#### response body to requester: NO NEED

#### response body to other users:

{"action": "meld", "roomId": 123, "userId": 123, "position": "A"}



### 12. history

#### request body: 

{"action": "history", "userId": 123}

#### response body:

{"action": "history", "userId": 123, "lostCount": 1, "ranking": 1, "username": "abcd", "winCount": 1}



### 13. Add AI player to a room

#### request body: 

{"action": "addAIPlayer", "roomId": 123}

#### response body:

{"action": "addAIPlayer", "AIPosition": "A", "roomId": 123}



### 14. AI Player

#### request body: 

{"action": "AIPlayerAction", "roomId": 123, "AIPosition": "A"}

#### response body:

Same as others.



### 15. Get all userId in a room

#### request body: 

{"action": "userListInRoom", "roomId": 123}

#### response body:

{"action": "userListInRoom", "roomId": 123, "positionA": 145, "positionB": "-", "positionC": "-", "positionD": "-"}
