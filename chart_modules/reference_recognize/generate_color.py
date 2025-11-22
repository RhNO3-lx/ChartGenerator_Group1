import numpy as np
if not hasattr(np, "asscalar"):
    np.asscalar = lambda x: x.item()

import random
from sklearn.cluster import KMeans
from colorsys import rgb_to_hls, hls_to_rgb
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import matplotlib.pyplot as plt

def visualize_palette(palette, bg_color=None, title="Color Palette"):
    """
    显示颜色调色板，可选背景色显示。
    
    参数:
        palette (List[List[int]]): 颜色列表，RGB格式
        bg_color (List[int] or None): 背景颜色（用于画布背景）
        title (str): 图像标题
    """
    n = len(palette)
    fig, ax = plt.subplots(figsize=(n * 1.2, 1.8))
    
    # 设置背景色
    if bg_color:
        fig.patch.set_facecolor(np.array(bg_color) / 255)
        ax.set_facecolor(np.array(bg_color) / 255)

    for i, color in enumerate(palette):
        rgb = np.array(color) / 255
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=rgb))
        ax.text(i + 0.5, -0.3, f"{color}", ha="center", va="center", fontsize=9)

    ax.set_xlim(0, n)
    ax.set_ylim(-0.5, 1)
    ax.axis('off')
    plt.title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig("/data/minzhi/code/ChartGalaxyDemo/modules_ChartGalaxyDemo/reference_recognize/1.png")


def rgb_to_lab(rgb):
    """将RGB转换为Lab颜色"""
    color_rgb = sRGBColor(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    return convert_color(color_rgb, LabColor)


def color_distance(c1, c2):
    """计算两个颜色的感知距离（Lab空间）"""
    return delta_e_cie2000(rgb_to_lab(c1), rgb_to_lab(c2))



def is_distinct(color, others, threshold=20, bg_color=None):
    """判断颜色是否与其他颜色以及背景足够区分"""
    for other in others:
        if color_distance(color, other) < threshold:
            return False
    if bg_color and color_distance(color, bg_color) < threshold:
        return False
    return True


def perturb_color(color, amount=15):
    """对颜色进行微调"""
    return [min(255, max(0, c + random.randint(-amount, amount))) for c in color]


def generate_new_colors(n, avoid_colors, bg_color):
    """生成与已有颜色和背景区分度高的新颜色"""
    result = []
    attempts = 0
    while len(result) < n and attempts < 500:
        candidate = [random.randint(0, 255) for _ in range(3)]
        if is_distinct(candidate, result + avoid_colors, bg_color=bg_color):
            result.append(candidate)
        attempts += 1
    return result

def rgb_to_hex(rgb_list):
    """
    将RGB列表转换为十六进制颜色代码
    :param rgb_list: 包含R,G,B三个整数的列表，例如 [202, 150, 229]
    :return: 十六进制颜色字符串，例如 "#ca96e5"
    """
    if len(rgb_list) != 3:
        raise ValueError("RGB列表必须包含3个元素[R,G,B]")
    
    r, g, b = rgb_list
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def generate_distinct_palette(data, main_colors, bg_color, num_colors=5):
    """
    生成颜色调色板，确保彼此区分，整体和谐，且和背景对比明显。
    
    参数:
        main_colors (List[List[int]]): 主色列表，每个颜色为RGB列表
        bg_color (List[int]): 背景颜色RGB
        num_colors (int): 目标调色板数量
        
    返回:
        List[List[int]]: 区分度高的颜色列表
    """
    main_colors = [list(map(int, c)) for c in main_colors]
    selected = []
    num_colors = len(data["colors"]["field"])

    # 1. 优先选择足够区分的主色
    for color in main_colors:
        if is_distinct(color, selected, bg_color=bg_color):
            selected.append(color)
        else:
            adjusted = perturb_color(color)
            if is_distinct(adjusted, selected, bg_color=bg_color):
                selected.append(adjusted)

        if len(selected) >= num_colors:
            selected =  selected[:num_colors]
            
            for i, field in enumerate(data["colors"]["field"].keys()):
                data["colors"]["field"][field] = rgb_to_hex(selected[i])
            
            for i, field in enumerate(data["colors_dark"]["field"].keys()):
                data["colors_dark"]["field"][field] = rgb_to_hex(selected[i])
            
            return data

    # 2. 如果不足，补全颜色
    remaining = num_colors - len(selected)
    new_colors = generate_new_colors(remaining, selected, bg_color)
    selected.extend(new_colors)

    for i, field in enumerate(data["colors"]["field"].keys()):
        data["colors"]["field"][field] = rgb_to_hex(selected[i])
    
    for i, field in enumerate(data["colors_dark"]["field"].keys()):
        data["colors_dark"]["field"][field] = rgb_to_hex(selected[i])
    print("data:",data)
    return data


# 示例调用
if __name__ == "__main__":
    main_colors = [[25, 33, 24], [234, 232, 216], [243, 228, 146], [100, 110, 99], [171, 172, 148]]
    bg_color = [255, 255, 255]
    palette = generate_distinct_palette(main_colors, bg_color, num_colors=6)

    print("Generated palette:", palette)
    visualize_palette({}, palette, bg_color, title="Generated Distinct Color Palette")