"""  
Copyright (c) 2019-present NAVER Corp.
MIT License
"""

# -*- coding: utf-8 -*-
import numpy as np
from skimage import io
import cv2

def enhance_image(img, BGR):
    assert BGR is True or BGR is False, f'Invalid argument: BGR must be True or False, got {BGR}'
    if not BGR:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.int32)

    val, cnt = np.unique(img, return_counts=True)
    med = cnt[np.argmin(np.abs(cnt - int(np.median(cnt))))]
    alpha = np.max(val[np.where(cnt == med)])

    # cụ thể cho giấy khai sinh
    # TODO khái quát hóa
    img = (img - alpha) * 3

    img = np.clip(img, 0, 255)
    img = img.astype(np.uint8)

    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def loadImage(img_file):
    img = io.imread(img_file)           # RGB order
    if img.shape[0] == 2: img = img[0]
    if len(img.shape) == 2 : img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:   img = img[:,:,:3]
    img = np.array(img)

    return img

def normalizeMeanVariance(in_img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
    # should be RGB order
    img = in_img.copy().astype(np.float32)

    img -= np.array([mean[0] * 255.0, mean[1] * 255.0, mean[2] * 255.0], dtype=np.float32)
    img /= np.array([variance[0] * 255.0, variance[1] * 255.0, variance[2] * 255.0], dtype=np.float32)
    return img

def denormalizeMeanVariance(in_img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
    # should be RGB order
    img = in_img.copy()
    img *= variance
    img += mean
    img *= 255.0
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def resize_aspect_ratio(img, square_size, interpolation, mag_ratio=1):
    """
    NOTE: ảnh đầu vào được resize giữ nguyên tỉ số
    Bước 1: Kích thước cạnh được nhân (giữ nguyên tỉ lệ) lên tối đa là mag_ratio lần kích thước ban đầu, nhưng không quá 1280
    Bước 2: Pad thêm 0 vào cạnh dưới và cạnh phải, sao cho 2 cạnh đều chia hết cho 32.
    :param img: ảnh RGB, shape (H, W, 3)
    :param square_size: kích thước (~ tối đa khi resize)
    :param interpolation:
    :param mag_ratio: nhân ảnh lên gấp bao nhiêu lần (không vượt quá cái ngưỡng square_size). Mặc định là giữ nguyên.
    :return: ảnh mới đã resize, tỉ lệ cạnh mới/cũ, kích thước của heatmap (1/2 kích thước ảnh đã resize)
    """
    height, width, channel = img.shape

    # magnify image size
    target_size = mag_ratio * max(height, width)

    # set original image size
    if target_size > square_size:
        target_size = square_size
    
    ratio = target_size / max(height, width)    

    target_h, target_w = int(height * ratio), int(width * ratio)
    proc = cv2.resize(img, (target_w, target_h), interpolation = interpolation)


    # make canvas and paste image
    target_h32, target_w32 = target_h, target_w
    if target_h % 32 != 0:
        target_h32 = target_h + (32 - target_h % 32)
    if target_w % 32 != 0:
        target_w32 = target_w + (32 - target_w % 32)
    resized = np.zeros((target_h32, target_w32, channel), dtype=np.float32)
    resized[0:target_h, 0:target_w, :] = proc
    target_h, target_w = target_h32, target_w32

    size_heatmap = (int(target_w/2), int(target_h/2))

    return resized, ratio, size_heatmap

def cvt2HeatmapImg(img):
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    return img
