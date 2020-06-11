# Test work BitMEX 
## Installation

    $ docker-compose up

## Quickstart
First af all you should create your Account 

Query example

    POST http://localhost:8000/account
    Accept: */*
    Cache-Control: no-cache
    Content-Type: application/json
    
    {
      "name": "Market",
      "api_key": "{api_key}",
      "api_secret": "{api_secret}"
    }    
     
####Create new order.

Query example:
    
    POST http://localhost:8000/orders/?account={account_name}
    Accept: */*
    Cache-Control: no-cache
    Content-Type: application/json

    {
      "orderType": "Market",
      "symbol": "XBTJPY",
      "orderQty": "1",
      "side": "Buy"
    }
