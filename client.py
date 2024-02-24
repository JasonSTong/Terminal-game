import asyncio
import os

import aioconsole
import websockets
from wcwidth import wcswidth
from colorama import Fore, Style, init

import json

init(autoreset=True)
commands = {
    "create_room": "create 创建房间 create+<room_name>",
    "change_name": "",
    "join_room": "join 加入房间 join+<room_id>",
    "leave_room": "leave 离开房间 leave",
    "send_room_message": "message 发送消息 message+<message>",
    "room_list": "list 查看房间列表 list",
    "clear_screen": "clear 清空当前屏幕 clear",
    "exit_program": "exit 退出程序 exit"
}
status_commands = {
    None: [commands["create_room"], commands["room_list"], commands["join_room"],
           commands["exit_program"], commands["clear_screen"]],
    "room": [commands["leave_room"], commands["send_room_message"],
             commands["clear_screen"], commands["exit_program"]]
}


def cprint(text, color=Fore.WHITE):
    if not text:
        return
    # 检查和替换文本
    red_keywords = ["错误:", "ERROR:"]
    green_keywords = ["成功:", "信息:", "INFO:", "info:"]
    if any(keyword in text for keyword in red_keywords):
        color = Fore.RED
    if any(keyword in text for keyword in green_keywords):
        color = Fore.GREEN
    print(color + text)


def async_run(func):
    asyncio.ensure_future(func)


def format_message(message_list: list = None):
    max_width = max(wcswidth(message) for message in message_list)
    border = '-' * (max_width + 4)
    result = border + '\n'
    for message in message_list:
        padding = max_width - wcswidth(message)
        result += f"| {message}{' ' * padding} |\n"
    result += border
    return result


def center_text(text, width):
    """ 将文本居中，并根据需要填充空格 """
    text_width = wcswidth(text)
    total_padding = width - text_width
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    return ' ' * left_padding + text + ' ' * right_padding


def left_align_text(text, width):
    """ 将文本左对齐，并根据需要填充空格 """
    text_width = wcswidth(text)
    padding = width - text_width
    return text + ' ' * padding


def generate_table_string(headers, rows, align_method=center_text):
    """ 生成一个表格字符串 """
    # 将每行的字符串分割成列表
    row_data = [row.split(' ') for row in rows]
    # row_data = [[item.strip() for part in row for item in part.split(',')] for row in row_data]

    # 计算每列的最大宽度
    column_widths = []
    for i in range(len(headers)):
        max_width = max(wcswidth(row[i]) for row in row_data)
        header_width = wcswidth(headers[i])
        column_widths.append(max(max_width, header_width))

    # 创建边框
    border = '+' + '+'.join('-' * (width + 2) for width in column_widths) + '+'

    # 构建表头
    header_row = '|' + '|'.join(align_method(headers[i], width + 2) for i, width in enumerate(column_widths)) + '|'
    table_string = border + '\n' + header_row + '\n' + border + '\n'

    # 构建数据行
    for row in row_data:
        row_str = '|'
        for i, item in enumerate(row):
            # 调用自定义函数来居中文本
            row_str += align_method(item, column_widths[i] + 2) + '|'
        table_string += row_str + '\n'

    # 添加底部边框
    table_string += border

    return table_string


class ClientMessage:
    @staticmethod
    def room_list(data):
        rooms = data['rooms']
        header = ["房间id", "房间名", "玩家数/最大玩家数"]
        infos = [f"{room['id']} {room['name']} {room['clients']}/{room['max_players']}" for room in rooms]
        if not infos:
            return "当前没有房间,请输入create进行创建"
        return generate_table_string(header, infos)

    @staticmethod
    def room_player_status(data):
        rooms = data['players']
        header = ["玩家id/名称", "分数", "是否房主"]
        infos = [f"{player.get('id')} {player['score']} {player['is_owner']}" for player in rooms]
        if not infos:
            return "当前没有玩家,已解散房间"
        return "\n" + generate_table_string(header, infos, left_align_text)

    @staticmethod
    def player_status(data):
        header = ["玩家id/名称", "剩余分数", "当前所在房间ID", "是否为房主"]
        infos = [f"{data['id']} {data['score']} {data['room_id']} {data['is_owner']}"]
        return generate_table_string(header, infos, left_align_text)

    @staticmethod
    def help(status=None):
        header = ["命令", "描述", "命令格式"]
        return generate_table_string(header, status_commands[status], left_align_text)


class PokerClient:
    def __init__(self):
        self.websocket = None
        self.uri = "ws://localhost:8765"
        self.room_id = None
        self.exit = False
        self.status = None

    async def send_action(self, action, data=None):
        if data is None:
            await self.websocket.send(json.dumps({"action": action}))
        else:
            await self.websocket.send(json.dumps({"action": action, **data}))

    async def connect(self):
        account = await aioconsole.ainput("Enter account: ")
        password = await aioconsole.ainput("Enter password: ")
        self.uri = f"{self.uri}?account={account}&password={password}"
        cprint("连接服务器中......")
        self.websocket = await websockets.connect(self.uri)
        await self.list_rooms()

    def sync_info(self, data):
        message = data['message']
        self.room_id = json.loads(message)['room_id']

    async def list_rooms(self):
        await self.websocket.send(json.dumps({"action": "list_rooms"}))

    async def room_info(self):
        await self.send_action("room_info", {"room_id": self.room_id})

    async def player_info(self):
        await self.send_action("player_info")

    async def logout(self):
        await self.websocket.send(json.dumps({"action": "logout"}))

    async def create_room(self, room_name):
        if self.room_id is None:
            try:
                max_players = int(await aioconsole.ainput("输入最大玩家数: "))
            except ValueError:
                cprint("ERROR: 请输入正确的玩家数")
                try:
                    max_players = int(await aioconsole.ainput("输入最大玩家数: "))
                except ValueError:
                    cprint("ERROR: 多次输入错误, 已自动退出.输入help查看帮助")
                    return
            await self.websocket.send(json.dumps({
                "action": "create_room",
                "room_name": room_name,
                "max_players": max_players
            }))
            self.status = "room"
        else:
            cprint("你已经加入一个房间了, 请先离开当前房间.")

    async def join_room(self, room_id):
        if self.room_id is None:
            await self.websocket.send(json.dumps({"action": "join_room", "room_id": room_id}))
            self.status = "room"
        else:
            cprint("你已经加入一个房间了, 请先离开当前房间.")

    async def leave_room(self):
        if self.room_id:
            await self.websocket.send(json.dumps({"action": "leave_room"}))
            self.status = None
        else:
            cprint("你还没有加入任何房间.")

    async def start_game(self):
        return await self.websocket.send(json.dumps({"action": "start_game"}))

    async def send_message(self, message):
        if self.room_id:
            await self.websocket.send(json.dumps({"action": "chat_message", "message": message}))
        else:
            cprint("你还没有加入任何房间.")

    async def change_name(self, name):
        await self.websocket.send(json.dumps({"action": "change_username", "username": name}))

    async def handle_messages(self):
        while not self.exit:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                if data["action"] == "room_list":
                    cprint(ClientMessage.room_list(data))
                if data["action"] == "player_info":
                    cprint(ClientMessage.player_status(data))
                elif data["action"] == "message":
                    cprint(f"{data['message']}")
                elif data["action"] == "room_status":
                    self.room_id = data["room_id"]
                    cprint(ClientMessage.room_player_status(data))
                elif data["action"] == "connected":
                    cprint(f"info: 连接服务器成功\n 客户端Id: {data['client_id']}\n")
                elif data["action"] == "hole_cards":
                    cprint(f"info: 你的手牌: {data['cards']}")
                elif data["action"] == "community_cards":
                    cprint(f"info: 公共牌: {data['cards']}")
                elif data["action"] == "winner":
                    cprint(f"info: 获胜者: {data['mes']}")
                elif data["action"] == "sync_info":
                    cprint(f"info: 正在同步信息...")
                    self.sync_info(data)
                elif data["action"] == "logout":
                    cprint(data["message"])
                    self.exit = True
                    raise KeyboardInterrupt
            except websockets.ConnectionClosed:
                cprint("info: Connection closed.")
            except KeyboardInterrupt:
                cprint("ERROR: 已被踢出连接")
            except Exception as e:
                cprint("ERROR: 接收到错误的服务器消息.请重新登录")

    async def command_loop(self):
        try:
            while not self.exit:
                await asyncio.sleep(0.1)
                command = await aioconsole.ainput("You: ")
                # 根据空格分段, 如果command开头不为'g' 仅分离第一个空格,后续空格不分离
                if command.startswith("g"):
                    command_list = command.split(" ", 3)
                else:
                    command_list = command.split(" ", 1)
                command = command_list[0]
                if len(command_list) == 2:
                    """
                        带参指令
                    """
                    info = command_list[1]
                    if len(info) < 1:
                        cprint(f"ERROR: 错误指令 {command} 或错误参数 <{info}> , 请重新输入")
                        continue
                    if command == "create":
                        await self.create_room(info)
                    elif command == "join":
                        await self.join_room(info)
                    elif command == "message":
                        await self.send_message(info)
                    elif command == "cname":
                        await self.change_name(info)
                    else:
                        cprint(f"ERROR: 错误指令 {command}, 输入help获取帮助")
                elif len(command_list) == 3:
                    """
                        多参指令
                    """
                    if command != "g":
                        cprint("ERROR: 错误指令 g, 输入help获取帮助")
                        continue
                    if command_list[1] == "bet":
                        try:
                            amount = int(command_list[2])
                        except ValueError:
                            if command_list[2] == "allin":
                                amount = "allin"
                            else:
                                cprint("ERROR: 请输入正确的金额")
                                continue
                        await self.websocket.send(json.dumps({"type": "bet", "amount": amount}))


                elif len(command_list) == 1:
                    """
                        无参指令
                    """
                    if command == "list":
                        await self.list_rooms()
                    elif command == "rinfo":
                        await self.room_info()
                    elif command == "pinfo":
                        await self.player_info()
                    elif command == "leave":
                        await self.leave_room()
                        self.room_id = None
                    elif command == "help":
                        cprint(ClientMessage.help(self.status))
                    elif command == "start":
                        cprint("信息: 开始游戏")
                        result = await self.start_game()
                        cprint(result)
                    elif command == "exit":
                        self.exit = True
                        async_run(self.logout())
                        raise KeyboardInterrupt
                    elif command == "clear":
                        if os.name == 'nt':
                            os.system("cls")
                        else:
                            os.system("clear")
                    else:
                        cprint(f"ERROR: 错误指令 {command}, 输入help获取帮助")
                else:
                    cprint("ERROR: 错误指令, 输入help获取帮助")
        except KeyboardInterrupt:
            cprint("info: 等待断开连接....")
        except Exception as e:
            async_run(self.logout())

    async def run(self):
        await self.connect()
        tasks = asyncio.gather(
            self.handle_messages(),
            self.command_loop(),
            return_exceptions=True
        )
        await tasks
        cprint("info: Disconnected from server.")


if __name__ == '__main__':
    client = PokerClient()
    asyncio.run(client.run())
# Function: ('', 'cprint')
# Function: ('', 'async_run')
# Function: ('', 'format_message')
# Function: ('', 'center_text')
# Function: ('', 'left_align_text')
# Function: ('', 'generate_table_string')
# Function: ('', 'room_list')
# Function: ('', 'room_player_status')
# Function: ('', 'player_status')
# Function: ('', 'help')
# Function: ('', '__init__')
# Function: ('async ', 'send_action')
# Function: ('async ', 'connect')
# Function: ('', 'sync_info')
# Function: ('async ', 'list_rooms')
# Function: ('async ', 'room_info')
