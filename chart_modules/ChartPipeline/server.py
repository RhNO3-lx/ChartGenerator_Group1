from flask import Flask, request, jsonify, Response, render_template
import re
import traceback
from pipeline import generate_variation, get_supported_chart_types
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # 渲染 templates/index.html
    return render_template('index.html')

@app.route('/chart', methods=['GET'])
def generate_chart():
    charttype = request.args.get('charttype', 'bar')
    data = request.args.get('data', 'test')

    try:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        svg = generate_variation(
            input_path=f"/data/lizhen/resources/result/data_pool_v4/{data}.json",
            output_path=f"output/{current_time}&{data}&{charttype}",
            temp_dir="temp",
            threads=1,
            chart_name=charttype
        )
        if svg is None:
            return jsonify({'error': 'no result'}), 400

        # 给所有 text 标签添加 class，方便前端样式控制和编辑
        svg = re.sub(r'<text', '<text class="editable-text"', svg)

    except Exception as e:
        return jsonify({'error': f'Unsupported: {e}, {traceback.format_exc()}'}), 400

    return Response(svg, mimetype='image/svg+xml')

@app.route('/chart-types', methods=['GET'])
def chart_types():
    data = request.args.get('data')
    if not data:
        return jsonify({'error': 'Missing data parameter'}), 400

    try:
        chart_types = get_supported_chart_types(data)
        return jsonify({'chartTypes': chart_types})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch chart types: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50185, debug=True)
