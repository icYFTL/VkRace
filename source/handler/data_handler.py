import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone
from source.database.database import Database
from source.vk_api.vk_api import VK
from source.utils.progress_bar import ProgressBar
from os import path, listdir
import cv2
from collections import OrderedDict
from halo import Halo
from source.utils.utils import get_last_result_name
from core import config


class DataHandler:
    def __init__(self, token: str):
        self.img_iterator = 0
        self.vk = VK(token=token)

    def run(self, delta='day') -> None:
        db = Database()
        if delta == 'day':
            delta = timedelta(days=1)
        elif delta == 'month':
            delta = timedelta(days=31)
        elif delta == 'year':
            delta = timedelta(days=365)
        elif delta == 'week':
            delta = timedelta(days=7)
        elif delta == 'hour':
            delta = timedelta(hours=1)
        else:
            raise ValueError('Invalid delta passed.')
        ts_left = db.get_min_ts()
        ts_right = (datetime.fromtimestamp(db.get_min_ts(), timezone('Europe/Moscow')) + delta).timestamp()
        me = self.vk.who_am_i()
        pb = ProgressBar(title='Drawing pics', end=db.get_total_messages())
        handled = 0
        result = {}
        color = 'red'

        while True:
            messages = db.get_messages_in(ts_left, ts_right)
            pb.update(handled)

            if datetime.fromtimestamp(ts_right, timezone('Europe/Moscow')) > datetime.now(timezone('Europe/Moscow')):
                break

            if not messages:
                ts_left = ts_right
                ts_right = (datetime.fromtimestamp(ts_right, timezone('Europe/Moscow')) + delta).timestamp()
                continue

            ts_left = ts_right
            ts_right = (datetime.fromtimestamp(ts_right, timezone('Europe/Moscow')) + delta).timestamp()

            for message in messages:
                if not result.get(message['conversation']):
                    result[message['conversation']] = 1
                else:
                    result[message['conversation']] += 1
            handled += len(messages)

            result = OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))

            self.draw_dgrams(list(result.keys()), list(result.values()),
                             str(datetime.fromtimestamp(ts_left, timezone('Europe/Moscow')).year))
        pb.stop()
        spinner = Halo(text='Making video...', spinner='dots')
        spinner.start()
        self.make_video()
        spinner.stop()

    def draw_dgrams(self, conversations, c_values, label, color='red') -> None:
        if len(conversations) < 2:
            return
        conversations = list([' '.join(x) for x in self.vk.get_sns(conversations)])[:10]
        c_values = c_values[:10]

        conversations.reverse()
        c_values.reverse()

        dpi = 80
        fig = plt.figure(dpi=dpi, figsize=(config['d_width'] / dpi, config['d_height'] / dpi))
        mpl.rcParams.update({'font.size': 9})

        plt.title('VK friends RACE')

        ax = plt.axes()
        ax.xaxis.grid(True, zorder=1)

        xs = range(len(conversations))

        plt.barh([x + 0.3 for x in xs], [d * 0.9 for d in c_values],
                 height=0.2, color=color, alpha=0.7, label=label,
                 zorder=2)

        plt.yticks(xs, conversations, rotation=10)

        plt.legend(loc='upper right')
        fig.savefig(path.join('pre_res', str(self.img_iterator)) + '.png')
        self.img_iterator += 1
        plt.close(fig)

    def make_video(self):
        image_folder = 'pre_res'
        video_name = get_last_result_name(config['delta'], config['fps'])
        video_path = 'out'

        images = [img for img in listdir(image_folder) if img.endswith(".png")]
        images = sorted(images, key=lambda x: int(x.replace('.png', '')))

        frame = cv2.imread(path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter(path.join(video_path, video_name), 0, 60, (width, height))
        video.fourcc(*'MP4V')

        for image in images:
            video.write(cv2.imread(path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()
