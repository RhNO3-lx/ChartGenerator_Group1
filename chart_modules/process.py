import os
import time
from datetime import datetime
from threading import Thread
import traceback
from pathlib import Path
import sys
project_root = Path(__file__).parent
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
print("sys.path:",sys.path)

from chart_modules.layout_extraction import get_compatible_extraction
from chart_modules.ChartGalaxy.example_based_generation.generate_infographic import InfographicImageGenerator
from chart_modules.reference_recognize.extract_chart_type import extract_chart_type
from chart_modules.reference_recognize.extract_main_color import extract_main_color
from chart_modules.generate_variation import generate_variation



def conduct_reference_finding(datafile, generation_status):
    print(conduct_reference_finding)
    datafile = os.path.join('processed_data', datafile.replace(".csv", ".json"))

    generation_status['step'] = 'find_reference'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False

    try:
        generation_status["extraction_templates"] = get_compatible_extraction(datafile)
        # print("筛选的模板:", generation_status["extraction_templates"])
        
        
        generation_status['status'] = 'completed'
        generation_status['completed'] = True
        

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print("find_reference 出错",e)
        
def conduct_layout_extraction(reference, datafile, generation_status):
    datafile = os.path.join('processed_data', datafile.replace(".csv", ".json"))
    reference = os.path.join('infographics', reference)

    # 保存选中的参考图片路径，供后续标题生成使用
    generation_status['selected_reference'] = reference

    generation_status['step'] = 'layout_extraction'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False
    # print("----------筛选的模板:", generation_status["extraction_templates"])

    try:
        # Step 1: 抽取参考风格
        generation_status['progress'] = '抽取参考信息图表风格...'
        generation_status['style']["colors"], generation_status['style']["bg_color"] = extract_main_color(reference)
        print("提取的颜色: %s %s", generation_status['style']["colors"], generation_status['style']["bg_color"])
        
        # Step 2: 执行图表类型分析 + 模板匹配
        generation_status['progress'] = '分析对应图表类型...'
        generation_status['style']['variation'] = extract_chart_type(reference, generation_status["extraction_templates"])
       
        
        for variation in generation_status['style']['variation']:
            print("variation:",variation)
            thread = Thread(target=generate_variation, args=(generation_status["selected_data"], 
                                                         f"buffer/{generation_status['id']}/{variation[0].split('/')[-1]}.svg", 
                                                         variation,
                                                         generation_status['style']["colors"],
                                                         generation_status['style']["bg_color"],))
            thread.start()
        
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print("conduct_layout_extraction 出错",e)
    
def conduct_title_generation(datafile, generation_status):

    generation_status['step'] = 'title_generation'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False

    try:
        # 生成单张标题图片
        generation_status['progress'] = '生成标题中...'
        generator = InfographicImageGenerator()
        generator.output_dir = f"buffer/{generation_status['id']}"

        # 获取参考图片路径（使用选中的reference图片）
        reference_image_path = generation_status.get('selected_reference', 'infographics/default.png')

        # 生成单张标题
        output_filename = f"buffer/{generation_status['id']}/title_0.png"
        result = generator.generate_single_title(
            csv_path=os.path.join('processed_data', datafile),
            reference_image_path=reference_image_path,
            output_filename=output_filename
        )

        # 存储当前标题信息
        generation_status['title_options'] = {
            'title_0.png': {
                'title_text': result['title_text'],
                'image_path': result['image_path'],
                'success': result['success']
            }
        }
        generation_status['current_title_text'] = result['title_text']

        print(f"Generated title: {result['title_text']}")
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print(f"title_generation 出错 {e} {traceback.format_exc()}")

def conduct_pictogram_generation(title, generation_status):
    generation_status['step'] = 'pictogram_generation'
    generation_status['status'] = 'processing'
    generation_status['progress'] = '生成配图中...'
    generation_status['completed'] = False

    try:
        # 生成单张配图
        generator = InfographicImageGenerator()
        generator.output_dir = f"buffer/{generation_status['id']}"

        # 获取当前标题文本
        title_text = generation_status.get('current_title_text', '')
        if not title_text and title in generation_status.get('title_options', {}):
            title_text = generation_status['title_options'][title].get('title_text', '')

        # 生成单张配图
        output_filename = f"buffer/{generation_status['id']}/pictogram_0.png"
        result = generator.generate_single_pictogram(
            title_text=title_text,
            colors=generation_status['style']['colors'],
            output_filename=output_filename
        )

        # 存储当前配图信息
        generation_status['pictogram_options'] = {
            'pictogram_0.png': {
                'pictogram_prompt': result['pictogram_prompt'],
                'image_path': result['image_path'],
                'success': result['success']
            }
        }

        print(f"Generated pictogram for: {title_text}")
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print(f"pictogram_generation 出错 {e} {traceback.format_exc()}")
    


# def simulate_final_generation(image_name):
#     global generation_status
    
#     steps = [
#         ('生成图表...', 1.5),
#         ('按照模板进行元素布局...', 2),
#         ('完成！', 0)
#     ]
    
#     generation_status['step'] = 'final_generation'
#     generation_status['status'] = 'processing'
#     generation_status['completed'] = False
    
#     for step, duration in steps:
#         generation_status['progress'] = step
#         time.sleep(duration)
    
#     generation_status['step'] = 'final_result'
#     generation_status['status'] = 'completed'
#     generation_status['completed'] = True
#     generation_status['image_name'] = image_name


# thread = Thread(target=generate_variation, args=("processed_data/App.json", 
#                                                          f"buffer/20251118080418_1491/d3-js/multiple pie chart/multiple_pie_chart_02.svg", 
#                                                          [
#         "d3-js/multiple pie chart/multiple_pie_chart_02",
#         [
#           "x",
#           "y",
#           "group"
#         ]
#       ],
#     [
#       [
#         227,
#         216,
#         131
#       ],
#       [
#         197,
#         200,
#         200
#       ],
#       [
#         28,
#         144,
#         248
#       ],
#       [
#         37,
#         86,
#         169
#       ],
#       [
#         18,
#         22,
#         24
#       ]
#     ],
#     [
#       245,
#       243,
#       239
#     ],))
# thread.start()