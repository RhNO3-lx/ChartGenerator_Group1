import csv
import json



# 定义要生成的顶层 JSON 结构的空模板
template = {
    "data": {
        "data": [],
        "columns": [
            # 会在后面自动填充
        ]
    },
    "chart_type": "",
    "data_format": {},
    "metadata": {
        "title": "",
        "description": "",
        "main_insight": "",
        "titles": {},
        "data_facts": []
    },
    "secondary_data": [],
    "variables": {},
    "typography": {
        "title": {"font_family": "", "font_size": "", "font_weight": ""},
        "description": {"font_family": "", "font_size": "", "font_weight": ""},
        "label": {"font_family": "", "font_size": "", "font_weight": ""},
        "annotation": {"font_family": "", "font_size": "", "font_weight": ""}
    },
    "datafacts": [],
    "titles": {
        "main_title": "",
        "sub_title": ""
    },
    "processed": False,
    "colors": {
        "field": {},
        "other": {},
        "available_colors": [],
        "background_color": "",
        "text_color": ""
    },
    "colors_dark": {
        "field": {},
        "other": {},
        "available_colors": [],
        "background_color": "",
        "text_color": ""
    }
}

def csv_to_json(input_csv, output_json):
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # 1) 生成 data.data 列表
        data_list = []
        for row in reader:
            # 对于每个字段，保留原值，缺失项自动为空字符串
            item = {headers[0]:row.get(headers[0], ""), "Units": row.get(headers[1], ""), "Category": headers[1]}
            data_list.append(item)
            item = {headers[0]:row.get(headers[0], ""), "Units": row.get(headers[2], ""), "Category": headers[2]}
            data_list.append(item)

        # 2) 生成 columns 元信息（name + 其余属性均为空串）
        #    你也可以根据需要自行调整 importance/description/unit/data_type/role
        columns_meta = []
        for h in headers:
            columns_meta.append({
                "name": h,
                "importance": "primary",
                "description": "",
                "unit": "none",
                "data_type": "",
                "role": ""
            })

    # 将填充好的内容合并到模板
    output = template.copy()
    output["data"]["data"] = data_list
    output["data"]["columns"] = columns_meta

    # 写入 JSON 文件
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    csv_to_json("/data/minzhi/code/ChartGalaxyDemo/processed_data/Transit.csv", "/data/minzhi/code/ChartGalaxyDemo/processed_data/Transit.json")
    # print(f"已生成 JSON 文件：{OUTPUT_JSON}")
