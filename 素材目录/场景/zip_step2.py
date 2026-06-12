import json
import os
import glob

def filter_data_elements(data_list):
    """过滤 data 数组，保留第一个元素在允许集合中的项"""
    allowed = {"stage", "face", "ev", "sd"}
    new_data = []
    for item in data_list:
        # 要求 item 是列表且至少有一个元素，且第一个元素为字符串且在 allowed 中
        if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str) and item[0] in allowed:
            new_data.append(item)
    return new_data

def process_json_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'scenes' in data and isinstance(data['scenes'], list):
        for scene in data['scenes']:
            if 'texts' in scene and isinstance(scene['texts'], list):
                for text_item in scene['texts']:
                    # 确保 text_item 是列表且长度 >= 6，且第6个元素（索引5）是字典且有 data 字段
                    if isinstance(text_item, list) and len(text_item) > 5:
                        target = text_item[5]
                        if isinstance(target, dict) and 'data' in target and isinstance(target['data'], list):
                            target['data'] = filter_data_elements(target['data'])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    input_dir = "./1"
    output_dir = "./2"
    os.makedirs(output_dir, exist_ok=True)

    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    if not json_files:
        print(f"未在 {input_dir} 目录下找到任何 .json 文件")
        return

    for input_path in json_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)
        try:
            process_json_file(input_path, output_path)
            print(f"已处理: {filename} -> {output_path}")
        except Exception as e:
            print(f"处理 {filename} 时出错: {e}")

if __name__ == "__main__":
    main()