from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from collections import Counter
import os
import pandas as pd
import openai
import requests
from pathlib import Path
import time
import json
from typing import List, Dict, Optional
from PIL import Image
import base64
import numpy as np
import cv2
from io import BytesIO
import sys

def get_background_color(image_path, edge_width=20):
    image = Image.open(image_path).convert('RGB')
    np_image = np.array(image)
    h, w, _ = np_image.shape

    # 提取四条边的像素，并 reshape 成 (N, 3)
    top = np_image[:edge_width, :, :].reshape(-1, 3)
    bottom = np_image[-edge_width:, :, :].reshape(-1, 3)
    left = np_image[:, :edge_width, :].reshape(-1, 3)
    right = np_image[:, -edge_width:, :].reshape(-1, 3)

    edges = np.vstack([top, bottom, left, right])  # shape: (N, 3)

    # 统计出现频率最高的颜色
    counts = Counter([tuple(p) for p in edges])
    background_color = counts.most_common(1)[0][0]
    return background_color

def color_distance(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

def extract_main_color(image_path, num_colors=6, bg_thresh=30, save_path=None):
    # 加载图像
    image = Image.open(image_path).convert('RGB')
    np_image = np.array(image)
    h, w, _ = np_image.shape
    pixels = np_image.reshape(-1, 3)

    # 提取背景色
    bg_color = get_background_color(image_path)

    # KMeans 聚类
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    counts = np.bincount(labels)

    # 排序（颜色按出现频率降序）
    sorted_idx = np.argsort(counts)[::-1]
    colors = colors[sorted_idx]
    counts = counts[sorted_idx]

    # 排除接近背景色的颜色
    filtered_colors = []
    filtered_counts = []
    for color, count in zip(colors, counts):
        if color_distance(color, bg_color) > bg_thresh:
            filtered_colors.append(color)
            filtered_counts.append(count)

    # print(filtered_colors)
    # 绘制饼图
    if filtered_colors:
        if save_path:
            plt.figure(figsize=(6, 6))
            bg_rgb = np.array(bg_color) / 255

            fig = plt.figure(figsize=(6, 6), facecolor=bg_rgb)
            ax = plt.gca()
            ax.set_facecolor(bg_rgb)
            filtered_colors = np.array(filtered_colors)
            hex_colors = ['#%02x%02x%02x' % tuple(c) for c in filtered_colors]
            plt.pie(filtered_counts, 
                    colors=filtered_colors / 255, 
                    # labels=hex_colors, 
                    startangle=90, 
                    counterclock=False, 
                    # autopct='%1.1f%%'
                    )
            # plt.title('Dominant Colors (Background Removed)')
            plt.savefig(save_path, bbox_inches='tight')
        # else:
        #     plt.show()
    else:
        print("未检测到非背景主色。")

    filtered_colors = [[int(i) for i in color] for color in filtered_colors]
    bg_color = [int(i) for i in bg_color]
    return filtered_colors, bg_color

def main():
    # 使用示例
    image_path = '/data/minzhi/code/ChartGalaxyDemo/infographics/by_author_@visualcapitalist_chart_8b926a819becbe35565821f56e0c1337a66ffbf16e9f7836607b75c5e1d3cc79.png'
    save_path = '/data/minzhi/code/output/pie.png'

    colors, bg = extract_main_color(
        image_path, num_colors=6, bg_thresh=30, save_path=save_path
    )
    print(colors, bg)

