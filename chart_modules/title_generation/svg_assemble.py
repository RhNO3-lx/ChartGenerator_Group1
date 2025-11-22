import xml.etree.ElementTree as ET
import re
import json
import os
import base64
import io
from PIL import Image
from pathlib import Path
from generate_full_image import get_image_only_title

def extract_info_from_svg(svg_path):
    """
    从SVG文件中提取标题文本和背景颜色
    
    参数:
        svg_path: SVG文件的路径
        
    返回:
        (title_text, background_color): 提取出的标题文本和背景颜色，如果未找到则相应值为None
    """
    # 1. 读取SVG文件内容
    try:
        svg_content = Path(svg_path).read_text(encoding='utf-8')
    except Exception as e:
        print(f"读取SVG文件时出错: {e}")
        return None, None
    
    # 注册SVG命名空间
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    # 2. 解析SVG内容
    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError as e:
        print(f"解析SVG内容时出错: {e}")
        return None, None
    
    # 提取标题
    title_text = extract_title(root)
    
    # 提取背景颜色
    background_color = extract_background_color(root)
    
    return title_text, background_color

def generate_title_image(title_text, background_color, image_resolution=(100, 100)):
    """
    根据标题文本和背景颜色生成标题图片
    """
    save_dir = "/data1/liduan/generation/chart/chart_pipeline/generate_title/title_images"
    save_path = os.path.join(save_dir, f"{title_text}.png")
    image_resolution = f"RESOLUTION_{image_resolution[0]}_{image_resolution[1]}"
    image_path = get_image_only_title(title_text, background_color,save_path, prompt_times = 1, image_times = 1, image_res = image_resolution)
    return save_path

def extract_title(root):
    """
    从SVG根元素中提取标题
    """
    # 3. 找到<g class="text">元素
    text_group = None
    for g_elem in root.findall(".//{http://www.w3.org/2000/svg}g"):
        if g_elem.get('class') == 'text':
            text_group = g_elem
            break
    
    if text_group is None:
        print("未找到<g class=\"text\">元素")
        return None
    
    # 4. 解析所有text元素及其font-size
    text_elements = []
    for text_elem in text_group.findall(".//{http://www.w3.org/2000/svg}text"):
        # 获取文本内容
        text_content = text_elem.text
        if text_content is None:
            # 检查是否有tspan子元素
            tspans = text_elem.findall(".//{http://www.w3.org/2000/svg}tspan")
            if tspans:
                text_content = ''.join(tspan.text or "" for tspan in tspans)
        
        if not text_content:
            continue
            
        # 获取font-size
        style = text_elem.get('style', '')
        font_size_match = re.search(r'font-size:\s*([0-9.]+)px', style)
        
        if font_size_match:
            font_size = float(font_size_match.group(1))
            text_elements.append((text_content, font_size))
    
    if not text_elements:
        print("未找到包含font-size的文本元素")
        return None
    
    # 5. 选择具有最大font-size的文本作为标题
    text_elements.sort(key=lambda x: x[1], reverse=True)
    print(text_elements)
    
    # 找出最大的font-size
    if text_elements:
        max_font_size = text_elements[0][1]
        # 提取所有具有最大font-size的文本元素
        largest_texts = [text for text, font_size in text_elements if font_size == max_font_size]
        title_text = " ".join(largest_texts)
    else:
        title_text = None
    
    return title_text

def extract_background_color(root):
    """
    从SVG根元素中提取背景颜色
    
    从<defs>元素中查找渐变定义，获取offset="0%"的stop-color作为背景颜色
    """
    # 查找所有defs元素
    defs = root.findall(".//{http://www.w3.org/2000/svg}defs")
    
    if not defs:
        print("未找到<defs>元素")
        return None
    
    # 在defs中查找所有渐变定义
    for def_elem in defs:
        # 线性渐变
        linear_gradients = def_elem.findall(".//{http://www.w3.org/2000/svg}linearGradient")
        for gradient in linear_gradients:
            # 查找offset="0%"的stop元素
            for stop in gradient.findall(".//{http://www.w3.org/2000/svg}stop"):
                if stop.get('offset') == '0%':
                    stop_color = stop.get('stop-color')
                    if stop_color:
                        return stop_color
        
        # 径向渐变
        radial_gradients = def_elem.findall(".//{http://www.w3.org/2000/svg}radialGradient")
        for gradient in radial_gradients:
            # 查找offset="0%"的stop元素
            for stop in gradient.findall(".//{http://www.w3.org/2000/svg}stop"):
                if stop.get('offset') == '0%':
                    stop_color = stop.get('stop-color')
                    if stop_color:
                        return stop_color
    
    print("未找到背景颜色定义")
    return None

def extract_background_color_from_base64image(base64_image):
    """
    从base64图像中提取背景颜色
    
    参数:
        base64_image: base64编码的图像字符串（不包含前缀如'data:image/png;base64,'）
        
    返回:
        背景颜色的十六进制表示，如'#RRGGBB'或'#RRGGBBAA'
    """
    try:
        # 将base64图像转换为PIL图像
        image = Image.open(io.BytesIO(base64.b64decode(base64_image)))
        
        # 转换为RGB模式（如果不是）
        if image.mode != 'RGB' and image.mode != 'RGBA':
            image = image.convert('RGB')
        
        # 获取图像的四个角和中心点的颜色
        width, height = image.size
        corners = [
            (0, 0),               # 左上角
            (width-1, 0),         # 右上角
            (0, height-1),        # 左下角
            (width-1, height-1),  # 右下角
        ]
        
        # 收集所有角落的颜色
        colors = []
        for x, y in corners:
            colors.append(image.getpixel((x, y)))
        
        # 检查四个角落的颜色是否一致
        if len(set(colors)) == 1:
            # 如果四个角落的颜色一致，则使用该颜色作为背景色
            background_color = colors[0]
        else:
            # 如果四个角落的颜色不一致，则考虑使用出现次数最多的颜色
            most_common_color = max(set(colors), key=colors.count)
            background_color = most_common_color
            
            # 或者计算颜色的平均值
            # average_color = tuple(int(sum(c[i] for c in colors) / len(colors)) for i in range(len(colors[0])))
            # background_color = average_color
        
        # 将颜色元组转换为十六进制字符串
        if len(background_color) == 3:  # RGB
            hex_color = '#{:02x}{:02x}{:02x}'.format(*background_color)
        elif len(background_color) == 4:  # RGBA
            hex_color = '#{:02x}{:02x}{:02x}{:02x}'.format(*background_color)
        else:
            raise ValueError(f"不支持的颜色格式: {background_color}")
        
        return hex_color
    
    except Exception as e:
        print(f"提取背景颜色时出错: {e}")
        return '#FFFFFF'  # 默认返回白色


# 原extract_title_from_svg函数保留，但调用新函数
def extract_title_from_svg(svg_path):
    """
    从SVG文件中提取标题文本（向后兼容）
    """
    title_text, _ = extract_info_from_svg(svg_path)
    return title_text

def extract_title_boundingbox_from_json(json_data):
    svg_bounding_box = json_data["bounding_box"]
    title_element = None
    for element in json_data["children"]:
        if element["tag"] == "g" and element.get("attributes",{}).get("class",{}) == "text":
            title_element = element
            break
    title_bounding_box = title_element["bounding_box"]
    title_bounding_box["x"] = title_bounding_box["x"] - svg_bounding_box["x"]
    title_bounding_box["y"] = title_bounding_box["y"] - svg_bounding_box["y"]
    return title_bounding_box

def add_title_image_to_svg(image_path, svg_content, title_bounding_box):
    """
    将标题图片添加到SVG内容中
    
    参数:
        image_path: 标题图片的路径
        svg_content: SVG文件内容
        title_bounding_box: 标题的边界框，包含x, y, width, height
        
    返回:
        修改后的SVG内容
    """
    # 注册SVG命名空间
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    # 解析SVG内容
    root = ET.fromstring(svg_content)
    
    # 找到并移除 <g class="text"> 元素
    text_group = None
    for g_elem in root.findall(".//{http://www.w3.org/2000/svg}g"):
        if g_elem.get('class') == 'text':
            text_group = g_elem
            parent = next(parent for parent in root.iter() if text_group in parent)
            parent.remove(text_group)
            break
    
    # 读取图片并转换为base64
    import base64
    from PIL import Image
    import io
    
    # # 获取图片格式
    # img_format = os.path.splitext(image_path)[1][1:].lower()
    # if img_format == 'jpg':
    #     img_format = 'jpeg'
    img_format = "png"
    
    
    # 读取图片并转换为base64
    print(image_path)
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    
    # 提取背景颜色
    bg_color = extract_background_color_from_base64image(b64_string)
    
    # 创建image元素
    image_elem = ET.Element('{http://www.w3.org/2000/svg}image')
    image_elem.set('x', str(title_bounding_box['x']))
    image_elem.set('y', str(title_bounding_box['y']))
    image_elem.set('width', str(title_bounding_box['width']))
    image_elem.set('height', str(title_bounding_box['height']))
    image_elem.set('href', f"data:image/{img_format};base64,{b64_string}")
    image_elem.set('preserveAspectRatio', 'xMidYMid meet')
    
    # 将图片元素添加到SVG根元素
    root.append(image_elem)

    # 把svg中顶层的rect元素的fill属性替换为bg_color
    for elem in root.findall("./{http://www.w3.org/2000/svg}rect"):
        elem.set('fill', bg_color)
    
    # 将修改后的SVG转换回字符串
    modified_svg = ET.tostring(root, encoding='unicode')
    
    
    return modified_svg

def process_folders():
    """
    遍历指定路径下的所有文件夹，处理每个文件夹中的chart.svg和convert_chart.json文件
    """
    base_path = "/data1/liduan/generation/chart/chart_pipeline/generate_title/from_yukai"
    results = []
    
    # 检查基础路径是否存在
    if not os.path.exists(base_path):
        print(f"基础路径不存在: {base_path}")
        return results
    
    # 获取所有子文件夹
    subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    print(f"找到 {len(subfolders)} 个子文件夹")
    
    for folder in subfolders:
        folder_path = os.path.join(base_path, folder)
        svg_path = os.path.join(folder_path, "chart.svg")
        json_path = os.path.join(folder_path, "convert_chart.json")
        
        # 检查文件是否存在
        svg_exists = os.path.exists(svg_path)
        json_exists = os.path.exists(json_path)
        
        if not svg_exists:
            print(f"文件夹 {folder} 中未找到 chart.svg 文件")
            continue
            
        if not json_exists:
            print(f"文件夹 {folder} 中未找到 convert_chart.json 文件")
            continue
        
        # 检查如果chart_with_title.svg存在，则跳过
        if os.path.exists(os.path.join(folder_path, "chart_with_title.svg")):
            print(f"文件夹 {folder} 中已存在 chart_with_title.svg 文件，跳过")
            continue
        
        print(f"处理文件夹: {folder}")
        
        # 提取SVG信息
        title, bg_color = extract_info_from_svg(svg_path)
        
        # # 读取JSON文件
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            # 提取SVG信息
            title_bounding_box = extract_title_boundingbox_from_json(json_data)
            if title_bounding_box["width"]/title_bounding_box["height"] > 2.0:
                continue
            print(title_bounding_box)
            # 解析JSON数据 - 留空，由用户自己实现
            parsed_json = {}  # 这里仅是占位符
            
            # 保存结果
            folder_result = {
                "folder": folder,
                "title": title,
                "background_color": bg_color,
                "json_data": json_data,
                "parsed_json": parsed_json
            }
            image_path = generate_title_image([title], bg_color, image_resolution=(title_bounding_box["width"], title_bounding_box["height"]))
            svg_content = add_title_image_to_svg(image_path, svg_content, title_bounding_box)
            # 把"ns1:"替换为"xlink:"
            svg_content = svg_content.replace("ns1:", "xlink:")
            with open(os.path.join(folder_path, "chart_with_title.svg"), "w", encoding='utf-8') as f:
                f.write(svg_content)
            print("output to ", os.path.join(folder_path, "chart_with_title.svg"))
            results.append(folder_result)
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {e}")
    
    print(f"成功处理了 {len(results)} 个文件夹")
    return results

if __name__ == "__main__":
    # 处理多个文件夹
    results = process_folders()
    
    # 示例：打印前三个结果的标题和背景颜色
    for i, result in enumerate(results[:3]):
        print(f"\n文件夹: {result['folder']}")
        print(f"标题: {result['title']}")
        print(f"背景颜色: {result['background_color']}")
    
    # 原示例代码保留为注释
    """
    # 使用示例
    import sys
    svg_path = "/data1/liduan/generation/chart/chart_pipeline/generate_title/svg/12__1746726402_circular_bar_chart_03_14121.svg"
    title, bg_color = extract_info_from_svg(svg_path)
    
    if title:
        print(f"提取的标题是: {title}")
    else:
        print("无法提取标题")
        
    if bg_color:
        print(f"提取的背景颜色是: {bg_color}")
    else:
        print("无法提取背景颜色")
    """
