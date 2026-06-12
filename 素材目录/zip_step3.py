import json
import os
import glob

def transform_text_entry(entry):
    """
    将原始 texts 中的单个条目（数组）转换为新格式的对象。
    原始格式: [character, null, text, null, number, { data: [...], env, ... }]
    新格式: { character: str, text: str, data: { key: { ... } } }
    """
    if not isinstance(entry, list) or len(entry) < 6:
        # 不符合预期格式，原样返回（或者可跳过）
        return entry

    character = entry[0] if entry[0] is not None else ""
    text = entry[2] if entry[2] is not None else ""
    extra = entry[5]
    
    data_obj = {}
    if isinstance(extra, dict) and "data" in extra and isinstance(extra["data"], list):
        for data_item in extra["data"]:
            if isinstance(data_item, list) and len(data_item) >= 3:
                key = data_item[0]  # 第一个字符串作为键，例如 "stage"
                config = data_item[2]  # 配置对象
                if isinstance(config, dict):
                    # 删除 action 字段
                    config.pop("action", None)
                data_obj[key] = config
            # 其他情况忽略
    return {
        "character": character,
        "text": text,
        "data": data_obj
    }

def process_json_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'scenes' in data and isinstance(data['scenes'], list):
        for scene in data['scenes']:
            if 'texts' in scene and isinstance(scene['texts'], list):
                new_texts = []
                for entry in scene['texts']:
                    new_entry = transform_text_entry(entry)
                    new_texts.append(new_entry)
                scene['texts'] = new_texts

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    input_dir = "./2"
    output_dir = "./3"
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