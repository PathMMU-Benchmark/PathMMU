from PIL import Image
import os
import shutil
import json


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data


def convert_tiff_to_jpeg(tiff_file_path, jpeg_file_path):
    with Image.open(tiff_file_path) as img:
        img = img.convert('RGB')
        img.save(jpeg_file_path, 'JPEG')


pathcls_img_dir = 'your_path/PathMMU/dataset_source/'   # your dir
data = load_data('data.json')
data_pathcls = data['PathCLS']

for subset, subset_data in data_pathcls.items():
    for qa in subset_data:
        if 'source_img' in qa.keys():
            dst_path = 'data/images/' + qa['img']
            src_path = pathcls_img_dir + qa['source_img']
            if src_path.split('.')[-1] in ['tif', 'tiff']:
                convert_tiff_to_jpeg(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)