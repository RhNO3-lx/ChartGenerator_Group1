from flask import Flask, render_template, jsonify, request, send_from_directory, Response
import pandas as pd
import os
import time
import random
import socket
import random
from threading import Thread
import traceback
import sys
import json
import re
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent  # 根据实际结构调整
sys.path.append("ChartPipeline")
# print(f"Python路径: {sys.path}")

from chart_modules.util import image_to_base64, find_free_port, get_csv_files, read_csv_data
from chart_modules.generate_variation import generate_variation
from chart_modules.process import conduct_reference_finding, conduct_layout_extraction, conduct_title_generation, conduct_pictogram_generation


app = Flask(__name__)

# 存储生成状态
generation_status = {
    'step': 'idle',
    'status': 'idle',
    'progress': '',
    'completed': False,
    'style': {},
    'selected_data': '',
    'selected_pictogram': '',
    'selected_title': '',  # 添加选中的标题信息
    "extraction_templates" : [],
    'id': ''
}

CACHE_FILE = "generation_status_cache.json"

def load_generation_status():
    """每次读取最新的 generation_status（如果文件不存在，则写入初始值）"""
    global generation_status
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                generation_status = json.load(f)
        except:
            pass
    else:
        # 第一次运行自动写入
        save_generation_status()

def save_generation_status():
    """每次更新 generation_status 都保存到 cache 中"""
    global generation_status
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(generation_status, f, indent=2, ensure_ascii=False)

def threaded_task(task_fn, *args):
    """
    线程用 wrapper：
    1) 先执行任务函数
    2) 任务函数结束之后保存 generation_status
    """
    global generation_status
    try:
        task_fn(*args)
    finally:
        save_generation_status()   # 👈 线程结束后更新 cache


@app.route('/authoring/generate_final')
def authoring():
    global generation_status
    # app.logger.debug("final generation_status")
    # app.logger.debug(generation_status)
    
    charttype = request.args.get('charttype', 'bar')
    datafile = request.args.get('data', 'test')
    title = request.args.get('title', '')
    pictogram = request.args.get('pictogram', '')
    
    return render_template('main.html', charttype = charttype, data = datafile, title = title, pictogram = pictogram)

@app.route('/authoring/chart', methods=['GET'])
def generate_chart():
    global generation_status
    charttype = request.args.get('charttype', 'bar')
    datafile = request.args.get('data', 'test')
    title = request.args.get('title', 'origin_images/titles/App_title.png')
    pictogram = request.args.get('pictogram', 'origin_images/pictograms/App_pictogram.png')

    app.logger.info(f"Chart type: {charttype}")
    app.logger.info(f"Data: {datafile}")
    
    try:
        title = f"buffer/{generation_status['id']}/{title}"
        pictogram = f"buffer/{generation_status['id']}/{pictogram}"
        img1_base64 = image_to_base64(title)
        img2_base64 = image_to_base64(pictogram)
        
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        print("generate_variation:",charttype, generation_status['style']["colors"], generation_status['style']["bg_color"])
        svg = generate_variation(
            input = f"processed_data/{datafile}.json",
            output = f"buffer/{generation_status['id']}",
            chart_template = charttype,
            main_colors = generation_status['style']["colors"],
            bg_color = generation_status['style']["bg_color"]
        )
        
        with open(f"buffer/{generation_status['id']}/{charttype}.svg", 'r', encoding='utf-8') as file:
            svg = file.read()

        if svg is None:
            return jsonify({'error': 'no result'}), 401

        # 给 <text> 标签添加 class，便于前端编辑
        svg = re.sub(r'<text', '<text class="editable-text"', svg)

        # 返回 JSON 字典
        return jsonify({
            'svg': svg,
            'img1': img1_base64,
            'img2': img2_base64
        })

    except Exception as e:
        app.logger.error(f'Unsupported: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Unsupported: {e}', 'trace': traceback.format_exc()}), 500

@app.route('/')
def index():
    csv_files = get_csv_files()
    return render_template('index.html', csv_files=csv_files)

@app.route('/api/data/<datafile>')
def get_data(datafile):
    data, columns = read_csv_data(datafile)
    return jsonify({
        'data': data,
        'columns': columns
    })

@app.route('/api/start_find_reference/<datafile>')
def start_find_reference(datafile):
    # 寻找适配的variation
    global generation_status
    load_generation_status()
    
    generation_status["selected_data"] = f'processed_data/{datafile.replace("csv","json")}'
    # generation_status['id'] = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_{random.randint(1000, 9999)}'
    generation_status['id'] = 'test_id'
    
    # 启动布局抽取线程
    thread = Thread(target = threaded_task, args=(conduct_reference_finding, datafile, generation_status,))
    thread.start()
    # save_generation_status()
    return jsonify({'status': 'started'})

@app.route('/api/start_layout_extraction/<reference>/<datafile>')
def start_layout_extraction(reference, datafile):
    # 寻找适配的variation
    global generation_status
    load_generation_status()
    app.logger.debug("generation_status")
    app.logger.debug(generation_status)
    
    # 启动布局抽取线程
    thread = Thread(target=threaded_task, args=(conduct_layout_extraction, reference, datafile, generation_status,))
    thread.start()

    return jsonify({'status': 'started'})

@app.route('/api/start_title_generation/<datafile>')
def start_title_generation(datafile):
    """生成标题图片"""
    global generation_status
    load_generation_status()
    # 需要开始保存生成的结果，创建一个ID
    
    # 启动布局抽取线程
    thread = Thread(target=threaded_task, args=(conduct_title_generation, datafile,generation_status,))
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/start_pictogram_generation/<title>')
def start_pictogram_generation(title):
    global generation_status
    load_generation_status()
    app.logger.debug(f"title_text:{title}")

    # 启动配图生成线程
    thread = Thread(target=threaded_task, args=(conduct_pictogram_generation, title, generation_status,))
    thread.start()

    return jsonify({'status': 'started'})

@app.route('/api/regenerate_title/<datafile>')
def regenerate_title(datafile):
    """重新生成单张标题图片"""
    global generation_status
    load_generation_status()

    # 启动标题重新生成线程
    thread = Thread(target=threaded_task, args=(conduct_title_generation, datafile, generation_status,))
    thread.start()

    return jsonify({'status': 'started'})

@app.route('/api/regenerate_pictogram/<title>')
def regenerate_pictogram(title):
    """重新生成单张配图图片"""
    global generation_status
    load_generation_status()

    # 启动配图重新生成线程
    thread = Thread(target=threaded_task, args=(conduct_pictogram_generation, title, generation_status,))
    thread.start()

    return jsonify({'status': 'started'})

# @app.route('/api/generate_final/<filename>')
# def generate_final_infographic(filename):
#     global generation_status
    
#     # 从请求中获取选择的标题索引
#     selected_title_index = request.args.get('selected_title_index', '0')
#     base_name = filename.replace('.csv', '')
    
#     # 普通处理：使用默认的图片名称
#     image_name = filename.replace('.csv', '.png')
    
#     # 检查图片是否存在
#     image_path = os.path.join('infographics', image_name)
#     if not os.path.exists(image_path):
#         return jsonify({'error': '对应的信息图表不存在'}), 404
    
#     # 启动最终生成线程
#     thread = Thread(target=simulate_final_generation, args=(image_name,))
#     thread.start()
    
#     return jsonify({'status': 'started'})

@app.route('/api/status')
def get_status():
    return jsonify(generation_status)

@app.route('/api/variation/selection')
def get_extraction_templates():
    global generation_status
    load_generation_status()
    # app.logger.debug(generation_status)
    return jsonify([item[0].split("/")[-1] for item in generation_status['style']['variation']])

@app.route('/api/references')
def get_references():
    """获取参考图：随机选择5张图片，第一张作为主要推荐"""
    other_infographics_dir = 'infographics'
    random_images = []

    if os.path.exists(other_infographics_dir):
        files = os.listdir(other_infographics_dir)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # 随机选择5张图片
        if len(image_files) >= 5:
            random_images = random.sample(image_files, 5)
        else:
            random_images = image_files  # 如果少于5张，就全部使用

    # 第一张作为主要推荐，其余4张作为备选
    main_image = random_images[0] if random_images else None
    other_images = random_images[1:5] if len(random_images) > 1 else []

    return jsonify({
        'main_image': main_image,
        'random_images': other_images
    })

@app.route('/api/titles')
def get_titles():
    """获取标题图片"""
    # 获取other_infographics目录中的所有图片
    global generation_status
    load_generation_status()
    # app.logger.debug(generation_status['title_options'])
    return jsonify(list(generation_status['title_options'].keys()))


@app.route('/api/pictograms')
def get_pictograms():
    """获取配图图片"""
    global generation_status
    load_generation_status()
    return jsonify(list(generation_status['pictogram_options'].keys()))

@app.route('/infographics/<filename>')
def serve_image(filename):
    return send_from_directory('infographics', filename)

@app.route('/origin_images/titles/<filename>')
def serve_origin_title(filename):
    return send_from_directory('origin_images/titles', filename)

@app.route('/generated_images/titles/<filename>')
def serve_generated_title(filename):
    return send_from_directory('generated_images/titles', filename)

@app.route('/origin_images/pictograms/<filename>')
def serve_origin_pictogram(filename):
    return send_from_directory('origin_images/pictograms', filename)

@app.route('/generated_images/pictograms/<filename>')
def serve_generated_pictogram(filename):
    return send_from_directory('generated_images/pictograms', filename)

@app.route('/other_infographics/<filename>')
def serve_other_infographic(filename):
    return send_from_directory('infographics', filename)

@app.route('/currentfilepath/<filename>')
def serve_static_file(filename):
    return send_from_directory(f'buffer/{generation_status["id"]}', filename)
            
@app.route('/static/<filename>')
def serve_file(filename):
    return send_from_directory(f'static', filename)
                      


if __name__ == '__main__':
    # 自动寻找可用端口
    free_port = find_free_port()
    print(f"Starting server on port {free_port}")
   
    app.run(debug=True, host='0.0.0.0', port=5176, use_reloader=False)
    