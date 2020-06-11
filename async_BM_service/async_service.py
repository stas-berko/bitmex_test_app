import asyncio
import hashlib
import hmac
import json
import time
import urllib.parse

import aiohttp


async def start_client_proxy(consume_ws, conn_detail):
    VERB = "GET"
    ENDPOINT = "/realtime"
    uri = f"wss://testnet.bitmex.com{ENDPOINT}?subscribe=instrument"
    session = aiohttp.ClientSession()
    async with session.ws_connect(uri) as server_ws:
        expires = int(time.time()) + 60 * 60 * 24
        signature = bitmex_signature(conn_detail["api_secret"], VERB, ENDPOINT, expires)
        request = {"op": "authKeyExpires", "args": [conn_detail["api_key"], expires, signature]}
        await server_ws.send_json(request)
        response = await server_ws.receive_json()
        async for msg in server_ws:

            if msg.type == aiohttp.WSMsgType.TEXT:
                data_json = json.loads(msg.data)
                data_json.update({"account": conn_detail["account"]})
                await consume_ws.send_json(data_json)

            elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                break


async def register_conn_with_retry(session, consumer_uri):
    while True:
        try:
            consume_ws = await session.ws_connect(consumer_uri)
            await consume_ws.send_json({"action": "register"})
            register_response = await consume_ws.receive_json()
            print(f"Try register {register_response}")
            if register_response["status"] == "ok":
                return consume_ws
        except aiohttp.client_exceptions.ClientConnectorError:
            continue


async def start_server_conn(consume_ws, task_q: asyncio.Queue):
    async for msg in consume_ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(f"NEW MESSAGE: <{msg.data}>")
            await task_q.put(json.loads(msg.data))
        elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
            break


async def bmx_server_conn(consume_ws, task_q):
    subs = {}
    while True:
        conn_detail = await task_q.get()
        if conn_detail["action"] == "subscribe":
            task = asyncio.create_task(start_client_proxy(consume_ws, conn_detail))
            print(f"Register {conn_detail['account']} task")
            subs[conn_detail["account"]] = task
        elif conn_detail["action"] == "unsubscribe":
            subs[conn_detail["account"]].cancel()
            print(f"Unregister {conn_detail['account']} task")


async def async_server():
    consumer_uri = "ws://bm_service:8000/ws/"
    session = aiohttp.ClientSession()
    consume_ws = await register_conn_with_retry(session, consumer_uri)
    print("Try setup connection")
    if consume_ws:
        task_queue = asyncio.Queue()
        await asyncio.gather(start_server_conn(consume_ws, task_queue), bmx_server_conn(consume_ws, task_queue))
    await session.close()


def bitmex_signature(apiSecret, verb, url, nonce, postdict=None):
    """Given an API Secret key and data, create a BitMEX-compatible signature."""
    data = ''
    if postdict:
        data = json.dumps(postdict, separators=(',', ':'))
    parsedURL = urllib.parse.urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query
    message = (verb + path + str(nonce) + data).encode('utf-8')

    signature = hmac.new(apiSecret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
    return signature


asyncio.get_event_loop().run_until_complete(async_server())
# {"action": "subscribe", "account": "admin"}
