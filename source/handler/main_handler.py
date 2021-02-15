from source.vk_api.vk_api import VK
from halo import Halo
from source.utils.progress_bar import ProgressBar
from source.database.database import Database
from os import path, mkdir
from source.handler import DataHandler
from core import config
from shutil import rmtree
from logging import getLogger


class MainHandler:
    def __init__(self, token: str):
        self.token = token
        self.vk = VK(token=self.token)
        self.log = getLogger('MainHandler')

    def run(self):
        if path.exists('pre_res'):
            self.log.warning('Folder pre_res already exists. Remove it? (y/n)')
            if input('> ').strip().lower() == 'y':
                rmtree('pre_res')
            else:
                self.log.info('Then try use --construct to create video from pre_res. Or clear it.')
                return

        if not path.exists('pre_res'):
            mkdir('pre_res')

        if not path.exists('out'):
            mkdir('out')

        if path.exists('database.db'):
            self.log.warning('Already have messages. Will update it.')

        spinner = Halo(spinner='dots', text='Getting chats...')

        spinner.start()
        conversations = self.vk.get_conversations()
        spinner.stop()

        handled = 0
        total = conversations[0]['count']
        self.log.info(f'Total chats: {total}')
        self.log.info(f'Loaded (uses only chats with users): {sum([len(x) for x in conversations])}')

        pb = ProgressBar(title='Messages getting', end=total)

        db = Database()
        for cell in conversations:
            for conversation in cell['items']:
                offset = 0
                id = conversation['conversation']['peer']['id']
                pb.update(handled)

                if db.is_conversation_exists(id):
                    offset = db.get_last_offset(id)
                else:
                    db.add_conversations(id)
                messages = self.vk.get_messages(conversation, offset)
                for msg in messages:
                    db.add_messages(msg)
                handled += 1
        DataHandler(self.token).run(config['delta'])
