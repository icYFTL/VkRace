from vk_api import VkApi, ApiError
from time import sleep
from logging import getLogger


class VK:
    def __init__(self, token=None):
        self.vk = VkApi(token=token)
        self.log = getLogger('VK')
        try:
            self.who_am_i()
        except ApiError:
            self.log.fatal('Invalid VK token passed')
            exit(-1)

    def get_conversations(self):
        result = []
        offset = 0
        while True:
            data = self.vk.method('messages.getConversations',
                                  {'offset': offset, 'count': 200, 'extended': 0})
            if not data['items']:
                break
            data['items'] = [x for x in data['items'] if x['conversation']['peer']['type'] == 'user' and x['conversation']['peer']['id'] != 100]
            sleep(0.4)
            offset += 200

            result.append(data)
        return result

    def get_messages(self, conversation, offset=0):
        while True:
            data = self.vk.method('messages.getHistory', {
                'offset': offset,
                'count': 200,
                'user_id': conversation['conversation']['peer']['id'],
                'extended': 0
            })
            offset += 200
            if not data['items']:
                break

            yield data, offset

    def who_am_i(self):
        return self.vk.method('users.get')[0]

    def get_sns(self, ids: list) -> tuple:
        ids = [str(x) for x in ids]
        return tuple([(x.get('first_name', None), x.get('last_name', None)) if x.get('first_name') and x.get('last_name') else None for x in self.vk.method('users.get', {'user_ids': ','.join(ids)})])


