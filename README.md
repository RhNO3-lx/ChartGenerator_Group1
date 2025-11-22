# 图表银河 - 信息图表生成器

这是一个基于Flask的精美网页应用，用于展示数据并生成信息图表。

## 功能特点

- 🎨 **精美的用户界面** - 现代化的渐变设计和流畅的动画效果
- 📊 **数据选择与预览** - 选择processed_data中的CSV文件并以表格形式展示
- 🚀 **智能生成流程** - 模拟真实的图表生成过程，包含多个步骤
- 🖼️ **结果展示** - 自动显示infographics文件夹中对应的PNG图片
- 📱 **响应式设计** - 适配不同屏幕尺寸

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 在浏览器中访问：
```
http://localhost:5000
```

## 使用方法

1. 在"数据选择与预览"区域选择一个数据集
2. 查看数据表格预览
3. 点击"生成信息图表"按钮
4. 等待生成过程完成（约5秒）
5. 查看生成的精美信息图表

## 文件结构

```
ChartGalaxyDemo/
├── app.py              # Flask应用主文件
├── requirements.txt    # Python依赖
├── templates/
│   └── index.html     # 主页模板
├── processed_data/     # CSV数据文件
└── infographics/      # PNG图片文件
```

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据处理**: Pandas
- **UI设计**: 现代化渐变设计 