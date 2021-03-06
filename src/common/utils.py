import os

import cv2
import numpy as np

from .config import RESULT_VIDEO_PARAMS


def create_writer(data_path, name, format=0):
    video_path = os.path.join(data_path, f'{name}.{RESULT_VIDEO_PARAMS["format"]["ext"]}')
    writer = cv2.VideoWriter(video_path,
                             cv2.VideoWriter_fourcc(*RESULT_VIDEO_PARAMS['format']['fourcc']),
                             RESULT_VIDEO_PARAMS['fps'],
                             RESULT_VIDEO_PARAMS['size'] if not format else RESULT_VIDEO_PARAMS['size'][::-1])
    return writer, video_path


def resize_image_with_ratio(image, w, h):
    new_image = np.zeros((h, w, 3), dtype='uint8')
    scale = min(w / image.shape[1], h / image.shape[0])
    resized = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)[:h, :w]
    y_start = max(new_image.shape[0] // 2 - resized.shape[0] // 2, 0)
    x_start = max(new_image.shape[1] // 2 - resized.shape[1] // 2, 0)
    new_image[y_start:y_start + resized.shape[0], x_start:x_start + resized.shape[1]] = resized
    return new_image
