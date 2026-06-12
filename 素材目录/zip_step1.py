import json
import os
import glob

def process_json_file(input_path, output_path):
    """处理单个JSON文件：裁剪scenes数组中的字段"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 如果存在scenes字段且为列表，则处理每一项
    if 'scenes' in data and isinstance(data['scenes'], list):
        new_scenes = []
        for scene in data['scenes']:
            # 只保留需要的字段，不存在的字段会被忽略
            filtered_scene = {
                key: scene[key] for key in ['label', 'nexts', 'texts', 'firstLine', 'title','selects']
                if key in scene
            }
            new_scenes.append(filtered_scene)
        data['scenes'] = new_scenes
    # 若无scenes字段，则原样保留（可根据需求改为跳过或报错）

    # 写入输出目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    input_dir = "./0"
    output_dir = "./1"
    os.makedirs(output_dir, exist_ok=True)

    # 查找所有json文件
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