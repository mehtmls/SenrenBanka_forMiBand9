import json
import os
import glob

def get_nested(data, path, default=None):
    """安全获取嵌套字典的值"""
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data

def deal_block(block, current_file, lang_index=2):
    temp_json = []
    temp_json.append({"type": "label", "name": block['label']})

    # ---------- 对话处理 ----------
    if isinstance(block.get('texts'), list):
        dialogue_group = None
        current_bg = ""
        current_img = ""

        for item in block['texts']:
            # 图片提取
            ev_file = face_file = stage_file = sd_file = None
            data = item.get('data', {})
            if get_nested(data, ['ev', 'redraw', 'imageFile', 'file']):
                ev_file = data['ev']['redraw']['imageFile']['file']
            if get_nested(data, ['face', 'redraw', 'imageFile', 'options']):
                obj=item['data']['face']['redraw']['imageFile']
                face_file =f"{obj['file'][:-6]}_face{obj['options']['face']}_{obj['options']['dress']}" #去除.stand
            if get_nested(data, ['stage', 'redraw', 'imageFile', 'file']):
                stage_file = data['stage']['redraw']['imageFile']['file']
            if get_nested(data, ['sd', 'redraw', 'imageFile', 'file']):
                sd_file = data['sd']['redraw']['imageFile']['file']

            img = sd_file or face_file
            bg = ev_file or stage_file

            # 角色与文本
            character = None
            text_list = item.get('text', [])
            if lang_index < len(text_list) and isinstance(text_list[lang_index], list):
                text = text_list[lang_index][1] if len(text_list[lang_index]) > 1 else ""
                character = text_list[lang_index][0] if len(text_list[lang_index]) > 1 else ""
            else:
                text = ""

            if not text and not character:
                continue

            if dialogue_group is None or bg != current_bg or img != current_img:
                current_bg = bg
                current_img = img
                if dialogue_group is not None:
                    temp_json.append(dialogue_group)
                dialogue_group = {
                    "type": "dialogue",
                    "background": bg,
                    "Img": img,
                    "dialogues": []
                }

            dialogue_group['dialogues'].append({
                "character": character,
                "text": text
            })

        if dialogue_group is not None:
            temp_json.append(dialogue_group)

    # ---------- 选项菜单 ----------
    if 'selects' in block and isinstance(block['selects'], list) and block['selects']:
        choices = []
        for sel in block['selects']:
            lang_data = sel.get('language', [])
            if lang_index < len(lang_data) and lang_data[lang_index] is not None:
                display_text = lang_data[lang_index].get('text', '')
            else:
                display_text = sel.get('text', '')
            target = sel.get('target', '')
            storage = sel.get('storage', current_file)
            opt = {"text": display_text, "target": target}
            if storage != current_file:
                opt["file"] = storage

            # 处理 exp 表达式 (如 SetBranchFlags(...))
            exp = sel.get('exp')
            if exp:
                opt["exp"] = exp

            choices.append(opt)
        temp_json.append({"type": "choices", "options": choices})

    # ---------- 跳转 / 条件分支 ----------
    else:
        nexts = block.get('nexts', [])
        if not nexts:
            temp_json.append({"type": "goto", "target": "", "file": None})
        elif len(nexts) == 1 and not nexts[0].get('eval'):
            n = nexts[0]
            target = n.get('target', '')
            storage = n.get('storage', current_file)
            goto = {"type": "goto", "target": target}
            if storage != current_file:
                goto["file"] = storage
            temp_json.append(goto)
        else:
            branches = []
            for n in nexts:
                branch = {"target": n.get('target', '')}
                storage = n.get('storage', current_file)
                if storage != current_file:
                    branch["file"] = storage
                if n.get('eval'):
                    branch["condition"] = n['eval']
                branches.append(branch)
            temp_json.append({"type": "branch", "branches": branches})

    return temp_json
def deal_files(input_path, output_path, lang_index=2):
    current_file = os.path.basename(input_path)[:-5]  # 去掉 .json 扩展名
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = []
    if 'scenes' in data and isinstance(data['scenes'], list):
        for scene in data['scenes']:
            result.extend(deal_block(scene, current_file, lang_index))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    input_dir = "./3"
    output_dir = "./4"
    lang_index = 2   # 简体中文
    os.makedirs(output_dir, exist_ok=True)
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    for input_path in json_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)
        deal_files(input_path, output_path, lang_index)
        print(f"已处理: {filename}")
    
if __name__ == "__main__":
    main()