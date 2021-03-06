import glob
import random
import time

import cv2

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message
from model import MusicModel
from utils import get_track_path, get_random_track


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message)
    start_time = time.time()
    send_message('Stage 3/4', message['tgbot']['user_id'])
    user_audio_paths = glob.glob(f'{message["tgbot"]["data_path"]}/audios/*')
    if message['tgbot']['music_recommendation'] and len(user_audio_paths) == 0:
        clips = []
        cap = cv2.VideoCapture(message['highlights']['highlight_path'])
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame = MUSIC_MODEL.preprocess(frame)
            clips.append(frame)
            if len(clips) == MUSIC_MODEL.deep:
                _ = MUSIC_MODEL.predict(clips)
                clips = []
        label = MUSIC_MODEL.get_label()
        audio_path = get_track_path(label)
        message.update({'music_recommendation': {'audio_path': audio_path,
                                                 'time': time.time() - start_time}})
        send_message(f'Stage 3/4, label: {label}, time: {message["music_recommendation"]["time"]:.2f}',
                     message['tgbot']['user_id'])
    else:
        message.update({'music_recommendation': {
            'audio_path': random.choice(user_audio_paths) if user_audio_paths else get_random_track(),
            'time': time.time() - start_time}
        })
        send_message(f'Stage 3/4, time: {message["music_recommendation"]["time"]:.2f}',
                     message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    MUSIC_MODEL = MusicModel('models/r3d_18_3x16x112x112', 'models/labels.txt')
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['music_recommendation'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
