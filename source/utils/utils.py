import logging
from os import path, mkdir, listdir
import json
from sys import stdout
import re
import hues


def log_prepare():
    if not path.exists('logs'):
        mkdir('logs')

    logging.basicConfig(handlers=(logging.FileHandler('logs/vk_race.log'), logging.StreamHandler(stdout)),
                        level=logging.INFO,
                        format=u'%(asctime)-15s | [%(name)s] %(levelname)s => %(message)s')


def config_prepare():
    if path.exists('config.json'):
        return json.load(open('config.json', 'r', encoding='UTF-8'))
    else:
        from configure import Configure

        Configure().run()
    return None


def get_last_result_name(delta, fps):
    template = 'result_{delta}_{fps}_fps_{counter}.mp4'
    counter = 0

    if path.exists('out'):
        files = sorted([x for x in listdir('out') if re.match(r'result_\w+_\d+_fps_\d+\.mp4', x)])
        if files:
            counter = int(files[-1].split('_')[4].replace('.mp4', '')) + 1

    return template.format(delta=delta, fps=fps, counter=counter)


def request(question: str, comparator=None, formatter=None, input_operator=input) -> str:
    while True:
        if formatter:
            formatter(question)
        else:
            print(question)
        result = input_operator('> ').strip()
        if comparator:
            if not comparator(result):
                hues.error('Invalid value passed.')
            else:
                return result
        else:
            return result


def yes_no(question: str, question_formatter=None) -> bool:
    question += ' (y/n)'
    while True:
        if not question_formatter:
            print(question)
        else:
            question_formatter(question)
        result = input('> ')
        if result.lower() not in ['y', 'n']:
            continue

        return result == 'y'
