import json
import pandas as pd

# 1. 读取JSON文件
def json_to_csv(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 提取嵌套的data数组
        records = data['data']['data']  # 根据实际JSON结构调整
        
        # 3. 转换为DataFrame
        df = pd.DataFrame(records)
        
        # 4. 保存为CSV
        df.to_csv(output_file, index=False)
        print(f"成功保存为CSV文件: {output_file}")
        
    except Exception as e:
        print(f"处理失败: {str(e)}")

# 使用示例
json_to_csv('/data/minzhi/code/ChartGalaxyDemo/processed_data/Crime.json', '/data/minzhi/code/ChartGalaxyDemo/processed_data/Crime.csv')