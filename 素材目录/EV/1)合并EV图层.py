import json
import re
from pathlib import Path
from PIL import Image

# 配置路径
EV_DIR = Path(r".\ev")
OUT_DIR = Path(r".\EV合并")

def group_layers(layers):
    """
    按图层名称前缀（A、B、C…）分组，每组包含：
    - base: name 以 'a' 结尾的图层（如 Aa）
    - children: 其他同前缀图层（如 Ab、Ac…）
    """
    groups = {}
    for layer in layers:
        name = layer.get("name")
        if not name or len(name) < 2:
            continue
        prefix = name[0]      # 'A', 'B', 'C'...
        suffix = name[1]      # 'a', 'b', 'c'...
        if prefix not in groups:
            groups[prefix] = {"base": None, "children": []}
        if suffix == 'a':
            groups[prefix]["base"] = layer
        else:
            groups[prefix]["children"].append(layer)
    # 移除没有 base 的组
    return {k: v for k, v in groups.items() if v["base"] is not None}

def process_scene(scene_dir: Path, json_path: Path):
    """处理单个场景目录"""
    scene_name = scene_dir.name
    out_scene_dir = OUT_DIR
    out_scene_dir.mkdir(parents=True, exist_ok=True)

    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    layers = config.get("layers", [])
    if not layers:
        print(f"[{scene_name}] 警告: JSON 中没有 layers 字段")
        return

    # 按名称分组
    groups = group_layers(layers)
    if not groups:
        print(f"[{scene_name}] 警告: 未找到有效的图层组（需要 Aa、Ba 等）")
        return

    # 辅助：通过 layer_id 获取图片路径
    def img_path(layer_id):
        return scene_dir / f"{layer_id}.png"

    # 处理每个组
    for prefix, group in groups.items():
        base_layer = group["base"]
        base_id = base_layer["layer_id"]
        base_img_file = img_path(base_id)
        if not base_img_file.exists():
            print(f"[{scene_name}] 组 {prefix} 缺少基础图片 {base_img_file}，跳过")
            continue

        # 读取基础图层（RGBA）
        base_img = Image.open(base_img_file).convert("RGBA")
        base_width, base_height = base_img.size

        # 输出基础图层单独文件：aa.png, ba.png, ca.png ...
        out_base = out_scene_dir / f"{scene_name[:5]}{prefix.lower()}a.png"
        base_img.save(out_base, "PNG")
        print(f"[{scene_name}] 生成 {out_base.name}")

        # 处理子图层
        for child in group["children"]:
            child_id = child["layer_id"]
            child_img_file = img_path(child_id)
            if not child_img_file.exists():
                print(f"[{scene_name}] 组 {prefix} 缺少子图片 {child_img_file}，跳过")
                continue

            # 获取叠加位置
            left = child.get("left", 0)
            top = child.get("top", 0)

            # 打开子图层
            child_img = Image.open(child_img_file).convert("RGBA")

            # 创建临时层并粘贴（使用 alpha 作为蒙版）
            overlay = Image.new("RGBA", (base_width, base_height), (0, 0, 0, 0))
            overlay.paste(child_img, (left, top), child_img)

            # 混合
            result = Image.alpha_composite(base_img, overlay)

            # 输出：前缀 + 子图层后缀（小写），如 ab.png, ac.png
            # 子图层名称第二个字符就是后缀，如 "Ab" -> 'b'
            suffix = child["name"][1].lower()
            out_child = out_scene_dir / f"{scene_name[:5]}{prefix.lower()}{suffix}.png"
            result.save(out_child, "PNG")
            print(f"[{scene_name}] 生成 {out_child.name}")

def main():
    if not EV_DIR.exists():
        print(f"错误: 目录 {EV_DIR} 不存在")
        return

    # 遍历所有子目录
    for scene_dir in EV_DIR.iterdir():
        if not scene_dir.is_dir():
            continue

        # 对应的 JSON 文件：父目录 / 目录名.json
        json_path = EV_DIR / f"{scene_dir.name}.json"
        if not json_path.exists():
            print(f"跳过 {scene_dir.name}：找不到 {json_path.name}")
            continue

        # 检查至少有一个图片文件（简单检查 2.png 是否存在？不一定总是 2，所以跳过预检，让处理时具体判断）
        print(f"\n处理场景: {scene_dir.name}")
        process_scene(scene_dir, json_path)

    print("\n批量处理完成！")

if __name__ == "__main__":
    main()