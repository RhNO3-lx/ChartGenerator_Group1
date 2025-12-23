import requests
import zipfile
import json
import os

# 创建测试JSON文件
test_data = {'test': 'zip_data', 'numbers': [10,20,30]}
with open('test_zip_content.json', 'w') as f:
    json.dump(test_data, f)

# 创建ZIP文件
with zipfile.ZipFile('test_upload.zip', 'w') as zf:
    zf.write('test_zip_content.json')

print('Test ZIP file created')

# 测试上传
try:
    with open('test_upload.zip', 'rb') as f:
        files = {'archive_file': ('test_upload.zip', f, 'application/zip')}
        data = {'archive_type': 'zip'}
        response = requests.post('http://127.0.0.1:5185/api/upload_archive', files=files, data=data)
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
finally:
    # 清理文件
    if os.path.exists('test_zip_content.json'):
        os.remove('test_zip_content.json')
    if os.path.exists('test_upload.zip'):
        os.remove('test_upload.zip')