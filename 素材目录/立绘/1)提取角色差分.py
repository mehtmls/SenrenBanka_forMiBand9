import os
import re
from PIL import Image
from collections import defaultdict

# ---------- 配置路径 ----------
BASE_FOLDER = r".\fgimage"   # fgimage 根目录
OUTPUT_FOLDER = r".\立绘提取"  # 输出目录

CANVAS_W = 1800
CANVAS_H = 2550

# ---------- 工具函数 ----------
def read_auto_encoding(path):
    """尝试多种编码读取文本文件"""
    for enc in ('shift_jis', 'cp932', 'utf-8-sig', 'utf-16', 'gbk'):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(path, encoding='utf-8', errors='ignore') as f:
        return f.read()

def parse_0txt(txt_path):
    """
    解析 _0.txt 文件，返回 {图层名: {id, left, top, width, height}}
    格式：id	name	left	top	width	height	unk	unk	unk	image_id
    """
    info = {}
    text = read_auto_encoding(txt_path)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 10 and parts[0].isdigit():
            name = parts[1].strip()
            if not name or name == '0':
                continue
            try:
                info[name] = {
                    'id': int(parts[9]),
                    'left': int(parts[2]),
                    'top': int(parts[3]),
                    'width': int(parts[4]),
                    'height': int(parts[5])
                }
            except ValueError:
                continue
    return info

def parse_info_groups(info_path, name_to_info):
    dress_groups = defaultdict(list)
    face_groups = defaultdict(list)
    current_dress = None
    text = read_auto_encoding(info_path)
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 4:
            continue
        if parts[0] == 'dress':
            current_dress = parts[1]
            layer_name = parts[4].strip()
            info = name_to_info.get(layer_name) or name_to_info.get(os.path.basename(layer_name))
            if info and info['id'] not in dress_groups[current_dress]:
                dress_groups[current_dress].append(info['id'])
        elif parts[0] == 'face':
            face_id = parts[1]
            layer_name = parts[3].strip()
            if current_dress is None:
                continue
            # 关键修改：将 '_' 替换为 '/' 后按 '/' 拆分
            for part in layer_name.replace("_","|").split('/'):
                part=part.replace('|', '/')
                info = name_to_info.get(part) or name_to_info.get(os.path.basename(part))
                if info and info['id'] not in face_groups[face_id]:
                    face_groups[face_id].append(info['id'])
    return dress_groups, face_groups
def find_src_file(img_dir, prefix, layer_id):
    """在指定目录下查找 {prefix}_0_{layer_id}.png"""
    path = os.path.join(img_dir, f"{prefix}_0_{layer_id}.png")
    if os.path.exists(path):
        return path
    # 兼容可能存在的 .tlg 文件（虽然新结构里应该都是 png）
    path = os.path.join(img_dir, f"{prefix}_0_{layer_id}.tlg")
    if os.path.exists(path):
        return path
    return None

def merge_layers(img_dir, prefix, layer_ids, name_to_info):
    """将一组 layer_id 按顺序合并到画布上，返回 Image"""
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    used = set()
    for lid in layer_ids:
        if lid in used:
            continue
        used.add(lid)
        src = find_src_file(img_dir, prefix, lid)
        if not src:
            print(f"  警告: 找不到图层 {prefix}_0_{lid} 在 {img_dir}")
            continue
        try:
            img = Image.open(src).convert("RGBA")
        except Exception as e:
            print(f"  错误: 无法打开 {src}: {e}")
            continue
        # 获取坐标
        layer_info = None
        for name, info in name_to_info.items():
            if info['id'] == lid:
                layer_info = info
                break
        if layer_info:
            left, top = layer_info['left'], layer_info['top']
        else:
            left, top = 0, 0
        canvas.paste(img, (left, top), img)
    return canvas

# ---------- 主流程 ----------
def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 1. 找到所有 _info.txt 文件（根目录下）
    info_files = []
    for f in os.listdir(BASE_FOLDER):
        if f.endswith('_info.txt') and os.path.isfile(os.path.join(BASE_FOLDER, f)):
            info_files.append(f)
    print(f"找到 {len(info_files)} 个 _info.txt 文件")

    # 2. 对每个变体（如 芳乃a, 芳乃b）进行处理
    for info_file in info_files:
        variant = info_file[:-9]   # 去掉 '_info.txt'，例如 '芳乃a'
        print(f"\n处理变体: {variant}")

        # 2.1 查找对应的 _0.txt 文件
        zero_txt_path = None
        img_dir = None
        # 递归搜索所有子目录（数字+角色名）下的 {variant}_0.txt
        for root, dirs, files in os.walk(BASE_FOLDER):
            for f in files:
                if f == f"{variant}_0.txt":
                    zero_txt_path = os.path.join(root, f)
                    img_dir = root   # 图片也在同一目录
                    break
            if zero_txt_path:
                break

        if not zero_txt_path:
            print(f"  错误: 找不到 {variant}_0.txt，跳过")
            continue

        print(f"  找到 _0.txt: {zero_txt_path}")

        # 2.2 解析 _0.txt 得到图层信息
        name_to_info = parse_0txt(zero_txt_path)
        if not name_to_info:
            print(f"  警告: {variant}_0.txt 无有效数据，跳过")
            continue
        print(f"  图层数: {len(name_to_info)}")

        # 2.3 解析 _info.txt 得到分组
        info_path = os.path.join(BASE_FOLDER, info_file)
        dress_groups, face_groups = parse_info_groups(info_path, name_to_info)
        print(f"  服装分组: {len(dress_groups)} 个")
        print(f"  表情分组: {len(face_groups)} 个")

        # 2.4 准备输出目录
        output_dir = os.path.join(OUTPUT_FOLDER, variant)
        dress_dir = os.path.join(output_dir, "dress")
        face_dir = os.path.join(output_dir, "face")
        os.makedirs(dress_dir, exist_ok=True)
        os.makedirs(face_dir, exist_ok=True)

        # 2.5 生成身体（body）——优先使用 '裸' 服装，否则取第一个
        if '裸' in dress_groups:
            body_dress = '裸'
        elif dress_groups:
            body_dress = list(dress_groups.keys())[0]
        else:
            print(f"  警告: 没有服装分组，跳过身体生成")
            body_dress = None

        #手动关闭body 生成
        body_dress = None
        if body_dress:
            body_layers = dress_groups[body_dress]
            print(f"  身体使用服装: {body_dress} ({len(body_layers)} 图层)")
            body_img = merge_layers(img_dir, variant, body_layers, name_to_info)
            body_path = os.path.join(output_dir, "body.png")
            body_img.save(body_path, "PNG")

        # 2.6 导出所有服装
        for dress, layers in dress_groups.items():
            print(f"  合并服装: {dress}")
            img = merge_layers(img_dir, variant, layers, name_to_info)
            safe_name = dress  # 保留原始日文名
            img.save(os.path.join(dress_dir, f"{safe_name}.png"), "PNG")

        # 2.7 导出所有表情
        print(face_groups)
        for face, layers in face_groups.items():
            print(f"  合并表情: {face},{layers}")
            img = merge_layers(img_dir, variant, layers, name_to_info)
            safe_name = face
            img.save(os.path.join(face_dir, f"{safe_name}.png"), "PNG")

    print("\n全部完成！")

if __name__ == "__main__":
    main()