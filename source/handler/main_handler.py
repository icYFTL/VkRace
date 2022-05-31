from source.vk import VK
from halo import Halo
from source.database.database import Database
from os import path, mkdir
from source.handler import DataHandler
from core import config
from shutil import rmtree
from logging import getLogger
import pickle
from source.utils import *


class MainHandler:
    def __init__(self, token: str):
        self.token = token
        self.vk = VK(token=self.token)
        self.log = getLogger('MainHandler')

    def get_conversations(self, save=True):
        conversations = None
        if path.exists(path.join('cache', 'peers.cache')):
            if yes_no('Have already loaded conversations. Wanna use them?'):
                with open(path.join('cache', 'peers.cache'), 'rb') as f:
                    conversations = pickle.load(f)
                    return conversations
        spinner = Halo(spinner='dots', text='Getting chats...')
        spinner.start()
        conversations = self.vk.get_conversations()

        if save:
            with open(path.join(path.join('cache', 'peers.cache')), 'wb') as f:
                pickle.dump(conversations, f)
        spinner.stop()
        return conversations

    def run(self):
        if path.exists('pre_res'):
            if yes_no('Folder pre_res already exists. Clear it?', self.log.warning):
                rmtree('pre_res')
                mkdir('pre_res')
            else:
                self.log.info('Then try use --construct to create video from pre_res. Or clear it manually.')
                exit(0)

        if not path.exists('pre_res'):
            mkdir('pre_res')

        if not path.exists('cache'):
            mkdir('cache')

        if not path.exists('out'):
            mkdir('out')

        if path.exists('database.db'):
            self.log.warning('Already have messages. Will update it.')
        conversations = self.get_conversations()

        handled = 0
        total = len(conversations)
        self.log.info(f'Total chats: {total}')

        pb = ProgressBar(title='Messages getting', end=total)

        db = Database()
        for cell in conversations:
            offset = 0
            pb.update(handled)

            if db.is_conversation_exists(cell):
                offset = db.get_last_offset(cell)
            else:
                db.add_conversations(cell)
            messages = self.vk.get_messages(cell, offset)
            db.add_messages(messages)
            handled += 1
        DataHandler(self.token).run(config['delta'])
