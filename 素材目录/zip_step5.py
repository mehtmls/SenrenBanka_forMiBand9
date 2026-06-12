import json
import os
import glob
import re

def clean_filename(filename):
    """
    清理文件名中的版本号后缀。
    例如: "001・アーサー王ver1.07.ks.json" -> "001・アーサー王.txt"
    规则: 去掉 ver数字.ks 或直接 .ks，再替换扩展名为 .txt
    """
    # 去掉扩展名 .json
    base = filename[:-5] if filename.endswith('.json') else filename
    # 去掉 ver数字.ks 后缀（如 "ver1.07.ks"）
    base = re.sub(r'ver[\d\.]+\.ks$', '', base)
    # 去掉残留的 .ks（如果没有 ver 数字）
    base = re.sub(r'\.ks$', '', base)
    # 加上 .txt
    return base + '.txt'

def clean_file_value(value):
    """
    清理 file 字段的值。
    例如: "015・ノーマルendver1.01.ks" -> "015・ノーマルend"
    规则: 去掉 ver数字.ks 或直接 .ks
    """
    if not isinstance(value, str):
        return value
    # 去掉 ver数字.ks 后缀
    cleaned = re.sub(r'ver[\d\.]+\.ks$', '', value)
    # 如果没匹配到 ver，则去掉末尾的 .ks
    cleaned = re.sub(r'\.ks$', '', cleaned)
    return cleaned

def traverse_and_clean(obj):
    if isinstance(obj, str):
        # 将字面量 \n 转换为真正的换行符
        obj = obj.replace('\\n', '\n')
        return obj
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == 'file' and isinstance(v, str):
                v = clean_file_value(v)
            new_obj[k] = traverse_and_clean(v)
        return new_obj
    elif isinstance(obj, list):
        return [traverse_and_clean(item) for item in obj]
    else:
        return obj
def process_file(input_path, output_dir):
    # 读取 JSON
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 清理所有 file 字段
    cleaned_data = traverse_and_clean(data)
    
    # 生成输出文件名（清理原文件名）
    input_filename = os.path.basename(input_path)
    output_filename = clean_filename(input_filename)
    output_path = os.path.join(output_dir, output_filename)
    
    # 写入输出文件（保持缩进）
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False)
    
    print(f"已处理: {input_filename} -> {output_filename}")

def main():
    input_dir = "./4"
    output_dir = "./5"
    os.makedirs(output_dir, exist_ok=True)
    
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    if not json_files:
        print(f"未在 {input_dir} 目录下找到任何 .json 文件")
        return
    
    for input_path in json_files:
        try:
            process_file(input_path, output_dir)
        except Exception as e:
            print(f"处理 {input_path} 时出错: {e}")

if __name__ == "__main__":
    main()