# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ActivityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = "follow_group"  # 모든 유저의 활동 상태를 공유할 그룹 이름

        # 그룹에 추가
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()  # WebSocket 연결 수락

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "update":
            await self.update_activity(data)

    async def update_activity(self, data):
        # 그룹에 브로드캐스트
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_activity_update",
                "user": self.user.username,
                "status": data["status"],  # 유저의 상태 (예: 'active', 'inactive')
            },
        )

    async def send_activity_update(self, event):
        # 브로드캐스트 메시지를 수신하고 클라이언트에 전송
        await self.send(
            text_data=json.dumps(
                {
                    "message": f"{event['user']} is now {event['status']}",
                    "user": event["user"],
                    "status": event["status"],
                }
            )
        )
