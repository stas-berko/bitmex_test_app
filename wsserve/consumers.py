import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from api.models import Account


def validate_row(data):
    if ("symbol" and "timestamp" and "lastPrice" ) in data:
        return {"symbol": data["symbol"], "timestamp": data["timestamp"],
                "price": data["lastPrice"]}


class ClientConsumer(AsyncWebsocketConsumer):
    group_name = "async_server"
    account = None

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        with open("test.yaml", "w") as f:
            print(self.group_name, self.account, file=f)

        if self.account:
            await self.channel_layer.group_discard(
                self.account,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("action") == "register":
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'send_connect_request',
                    'message': {"status": "ok"}
                }
            )

        elif text_data_json.get("action") == "subscribe":
            await self.subscribe_user(text_data_json)
        elif text_data_json.get("action") == "unsubscribe":
            await self.unsubscribe_user(text_data_json)
        else:
            account = text_data_json.get("account")
            await self.channel_layer.group_send(
                account,
                {
                    'type': 'send_message',
                    'message': text_data_json
                })

    async def subscribe_user(self, text_data_json):
        self.account = text_data_json.get("account")
        user = await self.get_account()
        if user:

            await self.channel_layer.group_add(
                self.account,
                self.channel_name
            )
            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'send_connect_request',
                    'message': {"api_key": user.api_key, "api_secret": user.api_secret,
                                "account": user.name, "action": "subscribe"}
                }
            )
        else:
            await self.close()

    async def unsubscribe_user(self, text_data_json):
        await self.channel_layer.group_discard(
            self.account,
            self.channel_name)
        await self.channel_layer.group_send(
            self.group_name, {
                'type': 'send_connect_request',
                'message': {"account": self.account, "action": "unsubscribe"}
            }
        )

    async def send_connect_request(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_account(self):
        return Account.objects.get(name=self.account)

    async def send_message(self, event):
        message = event['message']
        if data := message.get("data"):
            for data_item in data:
                if valid_data := validate_row(data_item):
                    valid_data.update({'account': message["account"]})
                    await self.send(text_data=json.dumps(valid_data))
