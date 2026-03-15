# TODO API DOCS

**REGISTER** (/register) (POST)
```
curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "EmailAddress": "example@example.com",
  "Password": "example",
  "Username": "example",
}'
```

**LOGIN** (/login) (POST)
```
curl -X 'POST' \
  'http://localhost:8000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "EmailAddress": "example@example.com",
  "Password": "example"
}'
```

**CREATE ITEM** (/create-item) (PUT)
```
curl -X 'PUT' \
  'http://localhost:8000/create-item' \
  --cookie "session_id=abc123;
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Title": "example",
  "Description": "example"
}'
```

**GET ITEMS** (/get-items) (GET)
```
curl -X 'GET' \
  'http://localhost:8000/get-items' \
  --cookie "session_id=abc123; \
  -H 'accept: application/json'
```

**EDIT ITEM** (/edit-item) (POST)
```
curl -X 'POST' \
  'http://localhost:8000/edit-item' \
  --cookie "session_id=abc123; \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "TodoItemID": 1,
  "Title": "example",
  "Description": "example"
}'
```

**TOGGLE COMPLETION** (/toggle-completion) (POST)
```
curl -X 'POST' \
  'http://localhost:8000/toggle-completion?ItemID=1' \
  --cookie "session_id=abc123; \
  -H 'accept: application/json' \
  -d ''
```

**DELETE ITEM** (/delete-item) (POST)
```
curl -X 'POST' \
  'http://localhost:8000/delete-item?ItemID=1' \
  --cookie "session_id=abc123; \
  -H 'accept: application/json' \
  -d ''
```
