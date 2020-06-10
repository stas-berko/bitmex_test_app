import asyncio
import aiohttp


async def hello():
    uri = "wss://testnet.bitmex.com/realtime?subscribe=instrument"
    consumer_uri = "ws://bm_service:8000/ws/"
    while True:
        try:
            session = aiohttp.ClientSession()
            async with session.ws_connect(uri) as server_ws, session.ws_connect(consumer_uri) as consume_ws:
                async for msg in server_ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await consume_ws.send_str(msg.data)
                    elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                        break
            break
        except aiohttp.client_exceptions.ClientConnectorError:
            await session.close()
            continue


asyncio.get_event_loop().run_until_complete(hello())
# {"action": "subscribe", "account": "STAS"}
