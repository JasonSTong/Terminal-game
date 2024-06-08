import json

from states.client_state import ClientSystem, ClientSystemEnum


class Client:
    def __init__(self, client_id, websocket, account, username, password):
        # 如果后期加入数据库, 可以将client_id改为uuid,暂时为自增
        self.client_id = client_id
        self.websocket = websocket
        self.room_id = None
        self.score = 1000  # 初始分数
        self.is_owner = False
        self.account = account
        self.username = username
        self.password = password
        self.client_state = ClientSystem()

    def get_username(self):
        return self.username

    def get_client_id(self) -> str:
        return self.client_id

    def get_id_or_name(self):
        return self.username or self.client_id

    def change_username(self, new_username):
        self.username = new_username
        return self.username

    def set_owner(self, is_owner):
        self.is_owner = is_owner

    def info(self):
        return f"客户端ID: {self.client_id} \n房间ID: {self.room_id} \n分数: {self.score} \n是否房主: {self.is_owner} \n用户名: {self.username}"

    async def send_message(self, info, action=None):
        if not action:
            action = "message"
        result = {
            "action": action,
        }
        if isinstance(info, dict):
            result.update(info)
        elif isinstance(info, str):
            result['message'] = info
        await self.websocket.send(json.dumps(result))

    async def logout(self):
        await self.websocket.close()

    async def other_login(self, websocket):
        if self.websocket.open:
            await self.websocket.send(
                json.dumps({'action': 'logout', 'message': f"客户端 {self.client_id} 已在其他地方登入。"}))
            await self.websocket.close()
        self.websocket = websocket
        await self.websocket.send(json.dumps({'action': 'sync_info', 'message': self.parse_json()}))

    def change_state(self, state: ClientSystemEnum):
        self.client_state.change_state(state)

    def parse_json(self):
        return json.dumps(
            {
                'id': self.client_id,
                'room_id': self.room_id,
                'score': self.score,
                'is_owner': self.is_owner,
                'username': self.username,
                'account': self.account,
                'state': self.client_state.state
            }
        )

    def client_info(self):
        return {
            'id': self.client_id,
            'name': self.username,
            'score': self.score,
            'room_id': self.room_id,
            'is_owner': self.is_owner
        }
