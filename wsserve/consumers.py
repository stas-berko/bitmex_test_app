import json
from channels.generic.websocket import AsyncWebsocketConsumer


def validate_row(data):
    if ("symbol" and "timestamp" and "lastPrice") in data:
        return {"symbol": data["symbol"], "timestamp": data["timestamp"], "price": data["lastPrice"]}


class ClientConsumer(AsyncWebsocketConsumer):
    group_name = "group"
    account = None

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("action") == "subscribe":
            self.account = text_data_json.get("account")
            if self.account:

                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
            else:
                await self.close()

        elif text_data_json.get("action") == "unsubscribe":
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name)
        else:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_message',
                    'message': text_data_json
                })

    async def send_message(self, event):
        message = event['message']
        if data := message.get("data"):
            for data_item in data:
                if valid_data := validate_row(data_item):
                    valid_data.update({"account": self.account})
                    await self.send(text_data=json.dumps(valid_data))
