import os
import json
import subprocess
import tempfile
from modules.chart_engine.utils.file_utils import create_temp_file, create_temp_dir, cleanup_temp_file, cleanup_temp_dir

import importlib
import logging

logger = logging.getLogger(__name__)

def html_to_svg(html_file, output_svg=None, width=1200, height=800):
    """
    Convert an HTML file with ECharts or D3.js to SVG using Puppeteer.
    Returns SVG content directly instead of saving to file.
    
    Args:
        html_file: Path to the HTML file
        output_svg: Optional path to save the SVG file (not used in this version)
        width: Width of the SVG
        height: Height of the SVG
    
    Returns:
        SVG content as string or None if conversion fails
    """
    # 创建Node.js脚本模板
    js_script = """
    const puppeteer = require('puppeteer');
    const fs = require('fs');
    const path = require('path');

    (async () => {
        const browser = await puppeteer.launch({
            headless: 'new',
            executablePath: '/usr/bin/google-chrome',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        await page.setViewport({ width: %d, height: %d });
        
        try {
            // 加载HTML文件
            await page.goto('file://' + path.resolve('%s'), { waitUntil: 'networkidle0' });
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 检查是否是ECharts图表
            const isECharts = await page.evaluate(() => {
                return typeof echarts !== 'undefined';
            });
            
            let svgContent;
            
            if (isECharts) {
                // ECharts特定处理
                await page.evaluate(() => {
                    const chart = echarts.getInstanceByDom(
                        document.querySelector('#chart-container')
                    );
                    if (chart) {
                        chart.setOption({animation: false});
                        try {
                            chart.setOption({renderer: 'svg'});
                        } catch (e) {
                            console.log('无法设置SVG渲染器:', e.message);
                        }
                    }
                });
                
                // 尝试从ECharts获取SVG
                svgContent = await page.evaluate(() => {
                    const chart = echarts.getInstanceByDom(
                        document.querySelector('#chart-container')
                    );
                    return chart ? chart.renderToSVGString() : null;
                });
            }
            
            // 回退到直接SVG提取
            if (!svgContent) {
                svgContent = await page.evaluate(() => {
                    const svg = document.querySelector('#chart-container svg');
                    if (!svg) return null;
                    
                    // 克隆并清理SVG
                    const clone = svg.cloneNode(true);
                    if (!clone.hasAttribute('width')) {
                        clone.setAttribute('width', svg.clientWidth);
                    }
                    if (!clone.hasAttribute('height')) {
                        clone.setAttribute('height', svg.clientHeight);
                    }
                    if (!clone.hasAttribute('viewBox')) {
                        clone.setAttribute('viewBox', `0 0 ${svg.clientWidth} ${svg.clientHeight}`);
                    }
                    return clone.outerHTML;
                });
            }
            
            // 最终回退 - 截图转SVG
            if (!svgContent) {
                const screenshot = await page.screenshot({encoding: 'base64'});
                svgContent = `<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg">
                    <image href="data:image/png;base64,${screenshot}" width="100%%" height="100%%"/>
                </svg>`;
            }
            
            // 输出SVG内容到stdout
            console.log(svgContent);
            
        } catch (error) {
            console.error('错误:', error);
            process.exit(1);
        } finally {
            await browser.close();
        }
    })();
    """
    
    # 格式化脚本参数（修复了参数数量问题）
    js_script = js_script % (
        width,  # 第一个 %d
        height,  # 第二个 %d
        html_file.replace('\\', '\\\\'),  # %s
        width,  # 第三个 %d (在回退SVG中)
        height   # 第四个 %d (在回退SVG中)
    )
    
    # 创建临时脚本文件
    js_file = create_temp_file(prefix="html_to_svg_", suffix=".cjs", content=js_script)
    
    try:
        # 确保puppeteer已安装
        try:
            subprocess.run(['npm', 'list', 'puppeteer'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("正在安装puppeteer...")
            subprocess.run(['npm', 'install', 'puppeteer'], check=True)
        
        # 运行脚本并捕获输出
        result = subprocess.run(
            ['node', js_file],
            check=True,
            capture_output=True,
            text=True
        )
        
        # 清理临时文件
        cleanup_temp_file(js_file)
        
        # 返回SVG内容
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"转换错误: {e.stderr}")
        cleanup_temp_file(js_file)
        return None
    except Exception as e:
        print(f"意外错误: {str(e)}")
        cleanup_temp_file(js_file)
        return None

def _save_to_file(content, output_file=None, prefix="", suffix=".html"):
    """
    Helper function to save content to a file, creating a temporary file if needed
    
    Args:
        content: Content to write to the file
        output_file: Path to save the file (optional)
        prefix: Prefix for temp filename
        suffix: Suffix for temp filename
        
    Returns:
        Path to the created file
    """
    if output_file is None:
        prefix = f"{prefix}_"
        output_file = create_temp_file(prefix=prefix, suffix=suffix, content=content)
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close()
    
    return output_file

def _get_dimensions(options, default_width=1200, default_height=800):
    """
    Helper function to extract width and height from options
    
    Args:
        options: Chart options
        default_width: Default width if not specified in options
        default_height: Default height if not specified in options
        
    Returns:
        Tuple of (width, height)
    """
    if not isinstance(options, dict) or "variables" not in options:
        return default_width, default_height
    
    width = options["variables"].get("width", default_width)
    height = options["variables"].get("height", default_height)
    return width, height

def _load_js_code(js_file, base_dirs=None):
    """
    Helper function to load JavaScript code from a file
    
    Args:
        js_file: Path to the JavaScript file (optional)
        base_dirs: List of base directories to search for JavaScript files
        
    Returns:
        String containing the JavaScript code
    """
    # If js_file is provided and exists, use it
    if js_file and os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    raise ValueError(f"No JavaScript file found for chart path: {js_file}. Please provide a valid JS file.")

def load_js_echarts(json_data=None, output_file=None, js_file=None, width=None, height=None):
    """
    Generate an ECharts chart using JavaScript.
    This function directly generates an HTML file with the JavaScript code.
    
    Args:
        json_data: Dict containing the JSON data for the chart
        output_file: Path to save the HTML output file (optional, will create a temp file if None)
        js_file: Path to the JavaScript file containing the make_option function
        
    Returns:
        Path to the generated HTML file
    """
    if json_data is None:
        raise ValueError("JSON data must be provided")
        
    # Default HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>ECharts Chart</title>
        <script src="%s"></script>
        <style>
            #chart-container {
                width: %dpx;
                height: %dpx;
            }
        </style>
    </head>
    <body>
        <div id="chart-container"></div>
        <script>
            // 立即初始化图表，使用SVG渲染器并禁用所有动画
            var chart = echarts.init(document.getElementById('chart-container'), null, {
                renderer: 'svg',
                animation: false,
                useUTC: true
            });
            
            // 禁用全局动画
            echarts.disableAllAnimation = true;
            
            // 准备数据
            const jsonData = JSON_DATA_PLACEHOLDER;
            
            JS_CODE_PLACEHOLDER
            
            // 创建图表选项
            let option;
            try {
                option = make_option(jsonData);
                
                // 禁用所有动画
                option.animation = false;
                option.animationDuration = 0;
                option.animationDurationUpdate = 0;
                option.animationDelay = 0;
                option.animationDelayUpdate = 0;
                
            } catch (e) {
                console.error("Error creating chart:", e);
                option = {
                    title: { text: "Error: " + e.message, left: 'center' }
                };
            }
            
            // 立即设置选项并渲染
            chart.setOption(option);
            
            // 导出SVG的优化函数
            function exportSvg() {
                try {
                    chart.setOption(option, {notMerge: true});
                    
                    const svgContent = chart.renderToSVGString();
                    
                    if (svgContent && svgContent.length > 0) {
                        const svgContainer = document.createElement('div');
                        svgContainer.id = 'svg-output';
                        svgContainer.style.display = 'none';
                        svgContainer.innerHTML = svgContent;
                        document.body.appendChild(svgContainer);
                    }
                } catch (e) {
                    console.error("Error exporting SVG:", e);
                }
            }
            
            // 立即尝试导出
            exportSvg();
            
            // 设置备用导出计时器，500ms后再尝试一次
            setTimeout(exportSvg, 500);
        </script>
    </body>
    </html>
    """
    
    # 获取本地库文件的绝对路径
    echarts_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'echarts.min.js'))
    
    # 使用文件协议的URL (用于SVG渲染)
    echarts_lib_url = f"file://{echarts_lib_path}"
    
    # Load JavaScript code
    if js_file:
        js_code = _load_js_code(js_file)
    else:
        js_code = f"""
        function make_option(jsonData) {{
            return JSON.parse(jsonData);
        }}
        """

    # Create HTML content
    formatted_html = html_template % (echarts_lib_url, width, height)
    formatted_html = formatted_html.replace('JSON_DATA_PLACEHOLDER', json.dumps(json_data))
    formatted_html = formatted_html.replace('JS_CODE_PLACEHOLDER', js_code)
    
    # Save the HTML to a file
    output_file = _save_to_file(formatted_html, output_file)    
    # 简化日志输出
    return output_file

def load_d3js(json_data=None, output_file=None, js_file=None, width=None, height=None):
    """
    Generate a D3.js chart using JavaScript.
    This function generates an HTML file with the D3.js code.
    
    Args:
        json_data: Dict containing the JSON data for the chart
        output_file: Path to save the HTML output file (optional, will create a temp file if None)
        js_file: Path to the JavaScript file containing the D3.js implementation
        
    Returns:
        Path to the generated HTML file
    """
    if json_data is None:
        raise ValueError("JSON data must be provided")
        
    # Default HTML template for D3.js - use %% to escape % characters
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>D3.js Chart</title>
        %s
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            #chart-container {
                width: 100%%;
                max-width: %dpx;
                height: %dpx;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
            }
        </style>
    </head>
    <body>
        <div id="chart-container"></div>
        <script>
            // 准备数据
            const json_data = JSON_DATA_PLACEHOLDER;

            // 导入utils.js
            UTILS_LIB_PLACEHOLDER
            
            // D3.js实现
            JS_CODE_PLACEHOLDER
            
            // 文档就绪时立即创建图表
            makeChart('#chart-container', json_data);
            
            // 500ms后检查SVG是否已生成
            setTimeout(function() {
                const svg = document.querySelector('#chart-container svg');
                if (svg) {
                    // 创建一个包含SVG内容的容器供提取使用
                    const svgContainer = document.createElement('div');
                    svgContainer.id = 'svg-output';
                    svgContainer.style.display = 'none';
                    svgContainer.innerHTML = svg.outerHTML;
                    document.body.appendChild(svgContainer);
                }
            }, 500);
        </script>
    </body>
    </html>
    """
    # 获取D3.js库文件的绝对路径
    d3_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'd3.min.js'))
    d3_voronoi_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'd3-voronoi-map.min.js'))
    d3_weighted_voronoi_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'd3-weighted-voronoi.min.js'))
    d3_sankey_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'd3-sankey.min.js'))
    d3_rough_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'svg2roughjs.umd.min.js'))
    # 使用文件协议的URL (用于SVG渲染)
    d3_lib_url = f"file://{d3_lib_path}"
    d3_voronoi_lib_url = f"file://{d3_voronoi_lib_path}"
    d3_weighted_voronoi_lib_url = f"file://{d3_weighted_voronoi_lib_path}"
    d3_sankey_lib_url = f"file://{d3_sankey_lib_path}"
    d3_rough_lib_url = f"file://{d3_rough_lib_path}"

    lib_urls = [d3_lib_url, d3_voronoi_lib_url, d3_weighted_voronoi_lib_url, d3_sankey_lib_url, d3_rough_lib_url]
    lib_urls_str = "\n".join([f"<script src='{url}'></script>" for url in lib_urls])

    utils_lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'lib', 'utils.js'))
    utils_code = _load_js_code(utils_lib_path)
    js_code = _load_js_code(js_file)
    # Create HTML content    
    formatted_html = html_template % (lib_urls_str, width, height)
    formatted_html = formatted_html.replace('JSON_DATA_PLACEHOLDER', json.dumps(json_data))
    formatted_html = formatted_html.replace('JS_CODE_PLACEHOLDER', js_code)
    formatted_html = formatted_html.replace('UTILS_LIB_PLACEHOLDER', utils_code)
    # Save the HTML to a file
    output_file = _save_to_file(formatted_html, output_file, prefix="_d3")
    # 简化日志输出
    return output_file

def render_chart_to_svg(json_data, \
                        js_file=None, width=None, height=None, \
                        framework="echarts", framework_type='js', html_output_path=None):
    """
    通用的图表渲染函数，支持多种图表框架
    
    Args:
        json_data (dict): 完整的JSON数据，包含图表数据和配置信息
        output_svg_path (str): SVG文件保存路径
        js_file (str, optional): JavaScript文件路径
        width (int, optional): 图表宽度(像素)
        height (int, optional): 图表高度(像素)
        framework (str): 使用的图表框架，可选"echarts"或"d3"
        html_output_path (str, optional): 保存中间HTML文件的路径
        
    Returns:
        Path to the generated SVG file
    """

    if width is None or height is None:
        w, h = _get_dimensions(json_data)
        width = width or w
        height = height or h
    
    if framework.lower() == "vegalite":
        # Use vegalite_py template
        template = js_file
        template_root = "modules.chart_engine.template.vegalite_py"
        general_chart_type = template.split('/')[-2]
        module_name = template.split('/')[-1].split('.')[0]
        # print("template_root: ", template_root)
        # print("general_chart_type: ", general_chart_type)
        # print("module_name: ", module_name)
        module_path = f"{template_root}.{general_chart_type}.{module_name}"
        # print(f"module_path: {module_path}")
        module = importlib.import_module(module_path)
        
        chart_words = module_name.split('_')
        chart_words = [word.capitalize() for word in chart_words]
        chart_type = ''.join(chart_words)
        
        template_class = getattr(module, chart_type)
        template_object = template_class(json_data)
        vega_spec = template_object.make_specification(json_data)
        
        vega_spec_file = create_temp_file(prefix="vega_spec_", suffix=".json", 
                                        content=json.dumps(vega_spec, indent=2))
        
        # try:
        svg_file, svg_content = template_object.specification_to_svg(vega_spec, output_svg_path)
        if svg_file is None:
            raise ValueError("SVG chart generation failed (returned None)")
        
        element_tree = template_object.svg_to_element_tree(svg_content)
        template_object.apply_variation(json_data)
        svg_file = output_svg_path
        svg_content = template_object.element_tree_to_svg(template_object.elements_tree)
        logger.info(f"VegaLite SVG chart generated successfully")
        return None, svg_content
        # except Exception as e:
        #     print(f"Error: {e}")
        #     return None
    
    # 为引擎创建临时目录，用于生成HTML文件
    temp_dir = create_temp_dir(prefix=f"{framework}_svg_")
    html_file = os.path.join(temp_dir, 'chart.html')

    try:
        # 根据框架类型生成HTML文件
        if framework.lower() == "echarts" and framework_type == 'js':
            load_js_echarts(json_data=json_data, output_file=html_file, js_file=js_file, width=width, height=height)
        elif framework.lower() == "echarts" and framework_type == 'py':
            template = js_file
            options = template.make_options(json_data)
            option_data = json.dumps(options)
            load_js_echarts(json_data=option_data, output_file=html_file, width=width, height=height)
        elif framework.lower() == "d3":
            load_d3js(json_data=json_data, output_file=html_file, js_file=js_file, width=width, height=height)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
        
        
        # 使用html_to_svg转换为SVG
        svg_content = html_to_svg(html_file, width=width, height=height)
        
        if svg_content is not None:
            # 简化日志输出，只返回路径，不打印
            return None, svg_content
        else:
            raise Exception(f"Failed to create SVG file from {framework.upper()} HTML")
    
    except Exception as e:
        print(f"Error load charts: {e}")
        return None
    
    finally:
        if os.path.exists(temp_dir):
           cleanup_temp_dir(temp_dir)

def render_vegalite_specification_to_svg(vegalite_specification, output_svg_path):
    import subprocess
    import json
    import os
    import random
    class NodeBridge:
        @staticmethod
        def execute_node_script(script_path: str, data: dict) -> str:
            # 生成一个随机种子
            random.seed(random.randint(0, 1000000))
            # 将数据写入临时JSON文件
            tmp_input = f'temp_input_{random.randint(0, 1000000)}.json'
            
            with open(tmp_input, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            # 执行Node.js脚本
            result = subprocess.run([
                'node', script_path, tmp_input
            ], capture_output=True, encoding='utf-8')
            # 清理临时文件
            os.remove(tmp_input)
            

            if result.returncode != 0:
                raise Exception(f"Node.js执行错误: {result.stderr}")

            return result.stdout
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'vegalite_py', 'vega_spec.js')
    result = NodeBridge.execute_node_script(script_path, {
        "spec": vegalite_specification,
    })
    # 把result写入output_svg_path
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(result)
    return output_svg_path
