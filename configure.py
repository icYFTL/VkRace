import json
from os import execl
from sys import executable, argv
from time import sleep
import hues
from screeninfo import get_monitors
from getpass import getpass


class Configure:
    def __init__(self, restart=True):
        self.restart = restart

    def __request(self, request: str, comparator, formatter=None, input_operator=input) -> str:
        while True:
            if formatter:
                formatter(request)
            else:
                print(request)
            result = input_operator('> ').strip().lower()
            if not comparator(result):
                hues.error('Invalid value passed.')
            else:
                return result

    def run(self) -> None:
        hues.info('### Configuring started ###')

        token = self.__request('VK token: ', lambda x: len(x) == 85, None, getpass)
        delta = self.__request('Delta (hour/day/week/month/year): ',
                               lambda x: x in ['hour', 'day', 'week', 'month', 'year'])

        fps_suj = 0
        if delta == 'hour':
            fps_suj = 60
        elif delta == 'day':
            fps_suj = 15
        elif delta == 'week':
            fps_suj = 7
        elif delta == 'month':
            fps_suj = 5
        elif delta == 'year':
            fps_suj = 1

        fps = self.__request(f'FPS ({fps_suj} is recommended): ', lambda x: 0 < int(x) < 120)
        clean = True if self.__request(f'Clear cache? (y/n): ',
                                       lambda x: x.lower().strip() in ['y', 'n']) == 'y' else False
        _display = get_monitors()
        if len(_display) > 1:
            _d_msg = '\n'.join(
                [f'#{i + 1} Display (width={obj.width}, height={obj.height})' for i, obj in enumerate(_display)])
            _d_i = self.__request(f'You have {len(_display)} monitors. Choose video resolution:\n{_d_msg}',
                                  lambda x: 1 <= int(x) < len(_display) + 1)
            display = _display[int(_d_i) - 1]

        _display = _display[0]
        d_width, d_height = _display.width, _display.height

        hues.info(f'Video resolution is ({d_width}, {d_height}) now.')

        result = {
            'token': token,
            'delta': delta,
            'fps': fps,
            'clean': clean,
            'd_width': d_width,
            'd_height': d_height
        }

        open('config.json', 'w', encoding='UTF-8').write(json.dumps(result))

        hues.info('### Configuring done ###')

        if self.restart:
            sleep(2)
            execl(executable, executable, *argv)
