#!/usr/bin/env python3
"""
图片筛选脚本
功能：
1. 删除横向图片（宽度*1.2 > 高度）
2. 删除高度小于1200的图片
3. 删除重复图片（基于文件内容MD5）
只保留竖向且高度 >= 1200 的唯一图片
"""

import os
import sys
import hashlib
from PIL import Image

def calculate_file_hash(file_path):
    """
    计算文件的MD5哈希值
    :param file_path: 文件路径
    :return: MD5哈希值字符串
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"  ⚠️  计算哈希失败: {str(e)}")
        return None

def filter_images(directory_path):
    """
    筛选图片文件
    :param directory_path: 图片目录路径
    """
    # 支持的图片格式
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    
    # 统计信息
    total_files = 0
    deleted_files = 0
    kept_files = 0
    error_files = 0
    duplicate_files = 0
    
    # 用于去重的哈希集合
    seen_hashes = set()
    
    print(f"开始处理目录: {directory_path}")
    print("=" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"错误：目录 '{directory_path}' 不存在！")
        return
    
    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # 跳过子目录
        if os.path.isdir(file_path):
            continue
            
        # 检查文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in image_extensions:
            continue
            
        total_files += 1
        
        try:
            # 首先检查是否为重复文件
            file_hash = calculate_file_hash(file_path)
            if file_hash is None:
                error_files += 1
                continue
                
            if file_hash in seen_hashes:
                os.remove(file_path)
                duplicate_files += 1
                deleted_files += 1
                print(f"处理: {filename} - ❌ 已删除 - 重复图片")
                continue
            
            # 打开图片获取尺寸
            with Image.open(file_path) as img:
                width, height = img.size
                
            print(f"处理: {filename} (尺寸: {width}x{height})")
            
            # 判断是否需要删除
            should_delete = False
            reason = ""
            
            # 检查是否为横向图片
            if width * 1.2 > height:
                should_delete = True
                reason = "横向图片"
            
            # 检查高度是否小于1200
            elif height < 1200:
                should_delete = True
                reason = "高度小于1200"
            
            if should_delete:
                os.remove(file_path)
                deleted_files += 1
                print(f"  ❌ 已删除 - {reason}")
            else:
                # 只有保留的图片才记录哈希值
                seen_hashes.add(file_hash)
                kept_files += 1
                print(f"  ✅ 保留")
                
        except Exception as e:
            error_files += 1
            print(f"  ⚠️  处理出错: {str(e)}")
    
    # 输出统计结果
    print("=" * 60)
    print("处理完成！")
    print(f"总文件数: {total_files}")
    print(f"已删除: {deleted_files}")
    print(f"  - 重复图片: {duplicate_files}")
    print(f"  - 不符合条件: {deleted_files - duplicate_files}")
    print(f"已保留: {kept_files}")
    print(f"处理出错: {error_files}")
    print("=" * 60)
    
    # 显示保留的图片信息
    if kept_files > 0:
        print("\n保留的图片详情：")
        print("-" * 40)
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                        print(f"{filename}: {width}x{height}")
                    except:
                        pass

def main():
    # 默认目录路径
    default_path = "other_infographics"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = default_path
    
    # 确认操作
    print(f"即将筛选目录: {directory_path}")
    print("筛选条件:")
    print("  - 删除重复图片（基于文件内容MD5）")
    print("  - 删除横向图片（宽度*1.2 > 高度）")
    print("  - 删除高度 < 1200 的图片")
    print("  - 保留竖向且高度 >= 1200 的唯一图片")
    print()
    
    confirm = input("确认执行？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消。")
        return
    
    # 执行筛选
    filter_images(directory_path)

if __name__ == "__main__":
    main() 