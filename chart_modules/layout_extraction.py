import os
import json
import random
from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.append(os.path.join(os.path.dirname(__file__), 'ChartPipeline'))

from chart_modules.ChartPipeline.modules.infographics_generator.template_utils import check_template_compatibility
from chart_modules.ChartPipeline.modules.chart_engine.template.template_registry import scan_templates

def get_compatible_extraction(data_path):
    generation_status = {}
    templates = scan_templates()
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return check_template_compatibility(data, templates)
