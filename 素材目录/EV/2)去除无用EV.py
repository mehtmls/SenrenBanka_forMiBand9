import os
import re
import glob
import json

def extract_image_basename(value):
    """
    从 JSON 字段值中提取图片基础名（不带扩展名，不带路径）。
    例如：
        "ev/神社_神社内d" -> "神社_神社内d"
        "芦花_face25h_私服" -> "芦花_face25h_私服"
        "sd/ムラサメ" -> "ムラサメ"
        "assets/murasame/dress/私服" -> "私服"（最后一段）
    """
    if not value:
        return None
    # 如果包含 '/' 则取最后一段
    if '/' in value:
        value = value.split('/')[-1]
    # 去掉可能的 .png 后缀（原 JSON 中一般没有，但安全起见）
    if value.endswith('.png') or value.endswith('.jpg'):
        value = os.path.splitext(value)[0]
    return value

def scan_json_files(json_dir):
    """扫描所有 JSON 文件，提取所有引用的图片基础名集合"""
    used_images = set()
    json_pattern = os.path.join(json_dir, "*.txt")  # step5 输出是 .txt
    for filepath in glob.glob(json_pattern):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 遍历每个指令
                for instr in data:
                    # 处理 background 字段（可能是字符串，可能不存在）
                    bg = instr.get('background')
                    if bg:
                        base = extract_image_basename(bg)
                        if base:
                            used_images.add(base)
                    # 处理 Img 字段
                    img = instr.get('Img')
                    if img:
                        base = extract_image_basename(img)
                        if base:
                            used_images.add(base)
                    # 处理 choices 中的图片？一般不涉及，暂不考虑
                    # 处理 branch 等也无图片
        except Exception as e:
            print(f"读取 {filepath} 失败: {e}")
    return used_images

def main():
    json_dir = r"..\场景\5"
    images_dir = r".\EV合并"
    
    if not os.path.isdir(images_dir):
        print(f"素材目录不存在: {images_dir}")
        return
    
    used_set = scan_json_files(json_dir)
    print(f"共找到 {len(used_set)} 个被引用的图片文件名:")
    # 可选: 打印前20个
    for name in list(used_set)[:20]:
        print(f"  {name}")
    
    # 扫描素材目录中的所有 .png 文件
    all_files = glob.glob(os.path.join(images_dir, "*.png"))
    # 提取文件名（不含扩展名）
    all_basenames = {}
    for f in all_files:
        basename = os.path.splitext(os.path.basename(f))[0]
        all_basenames[basename] = f
    
    # 找出未引用的文件
    unused = []
    for basename, fullpath in all_basenames.items():
        if basename not in used_set:
            unused.append(fullpath)
    
    print(f"\n素材目录中共有 {len(all_files)} 个 PNG 文件")
    print(f"未引用的文件数量: {len(unused)}")
    
    if unused:
        print("以下文件未被任何 JSON 引用，将被删除：")
        for f in unused[:30]:  # 显示前30个
            print(f"  {os.path.basename(f)}")
        if len(unused) > 30:
            print(f"  ... 还有 {len(unused)-30} 个")
        
        confirm = input("\n确认删除这些未引用文件？(y/N): ")
        if confirm.lower() == 'y':
            for f in unused:
                try:
                    os.remove(f)
                    print(f"已删除: {os.path.basename(f)}")
                except Exception as e:
                    print(f"删除失败 {f}: {e}")
            print("清理完成")
        else:
            print("取消删除")
    else:
        print("所有素材均被引用，无需清理")

if __name__ == "__main__":
    main()