from vk_api import VkApi, ApiError
from vk_api.execute import VkFunction
from time import sleep
from logging import getLogger
from .utils import *


class Scripts:
    def __init__(self):
        with open('source/vk/execute/get_messages.js', 'r', encoding='UTF-8') as f:
            self.get_messages = f.read()
        with open('source/vk/execute/get_peers.js', 'r', encoding='UTF-8') as f:
            self.get_peers = f.read()


class VK:
    def __init__(self, token=None):
        self.vk = VkApi(token=token)
        self.log = getLogger('VK')
        self.scripts = Scripts()
        try:
            self.who_am_i()
        except ApiError:
            self.log.fatal('Invalid VK token passed')
            exit(-1)

    def get_conversations(self, api_limit=15):
        offset = 0
        total_count = 200
        result = []
        while offset < total_count:
            code = set_args(self.scripts.get_peers,
                            offset=offset,
                            total_count=total_count,
                            api_limit=api_limit)
            try:
                func = VkFunction(code=code)
                data = func(self.vk)
            except Exception as e:
                self.log.warning('Conversations getter decided to chill... Restoring it, give me a second...')
                if api_limit - 5 >= 5:
                    api_limit -= 5
                continue

            offset = data['Offset']
            total_count = data['TotalCount']
            if data['Peers']:
                result.extend([x['conversation']['peer']['id'] for x in data['Peers'] if
                               x['conversation']['peer']['type'] == 'user'])

        return result

    def get_messages(self, peer_id: int, offset=0, api_limit=25):
        # data = self.vk.method('messages.getHistory', {
        #     'offset': offset,
        #     'count': 200,
        #     'user_id': conversation['conversation']['peer']['id'],
        #     'extended': 0
        # })
        offset = offset
        total_count = offset + 1  # XDXD
        result = []
        while offset < total_count:
            code = set_args(self.scripts.get_messages, total_count=total_count, user_id=peer_id, offset=offset, api_limit=api_limit)

            func = VkFunction(code=code)
            data = func(self.vk)

            offset = data['Offset']
            total_count = data['TotalCount']
            if data['History']:
                result.extend(data['History'])

        return result

    def who_am_i(self):
        return self.vk.method('users.get')[0]

    def get_sns(self, ids: list) -> tuple:
        ids = [str(x) for x in ids]
        return tuple([(x.get('first_name', None), x.get('last_name', None)) if x.get('first_name') and x.get(
            'last_name') else ('Удаленный', 'пользователь') for x in
                      self.vk.method('users.get', {'user_ids': ','.join(ids)})])
