import argparse
from source.handler.data_handler import DataHandler
from source.handler.main_handler import MainHandler
from core import config


def get_args():
    parser = argparse.ArgumentParser('VkRace statistic tool')
    parser.add_argument('--configure', help='Run configure tool (for local computing)', action='store_true')
    parser.add_argument('--no_update', help='Run script without database updating', action='store_true')
    parser.add_argument('--construct', help='Construct video from existing images in pre_res folder',
                        action='store_true')
    args = parser.parse_args()
    return args


def handle_args():
    args = get_args()

    if args.configure:
        from configure import Configure

        Configure(False).run()
    elif args.no_update:
        DataHandler(config['token']).run(config['delta'])
    elif args.construct:
        DataHandler(config['token']).make_video()
    else:
        MainHandler(config['token']).run()

