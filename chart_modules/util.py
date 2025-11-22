import base64
from flask import jsonify
from datetime import datetime
import traceback
import re
import os
import socket
import pandas as pd
import json

# 获取processed_data文件夹中的所有CSV文件
def get_csv_files():
    csv_files = []
    data_dir = 'processed_data'
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
    print(f"csv_files:{csv_files}")
    return csv_files

# 读取CSV文件内容
def read_csv_data(filename):
    try:
        filepath = os.path.join('processed_data', filename)
        df = pd.read_csv(filepath)
        print(df)
        return df.to_dict('records'), list(df.columns)
    except Exception as e:
        print(f"Error reading CSV file {filename}: {e}")
        return [], []


def image_to_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
        # 返回 data URI，前端可直接作为 <img src="..."> 使用
        ext = os.path.splitext(path)[-1][1:]  # 取后缀
        return f"data:image/{ext};base64,{encoded}"
    
def find_free_port(start_port=5000):
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            port += 1