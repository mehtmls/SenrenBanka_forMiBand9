import os
from PIL import Image

# ===== 配置 =====
INPUT_DIR = r".\立绘提取"    # 图层库根目录
OUTPUT_DIR = r".\立绘裁切"# 裁剪输出根目录

CROP_W = 850//2          # 裁剪宽度
CROP_H = 2169//2         # 裁剪高度 (2550 - 381)
LEFT = (1800 - CROP_W) // 2   # (1800-850)//2 = 475
TOP = 381
RIGHT = LEFT + CROP_W          # 475+850 = 1325
BOTTOM = TOP + CROP_H          # 381+2169 = 2550
TARGET_W = 192
TARGET_H = 490
# =================

def process_file(src_path, dst_path):
    img = Image.open(src_path).convert("RGBA")
    cropped = img.crop((LEFT, TOP, RIGHT, BOTTOM))
    resized = cropped.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    resized.save(dst_path, "PNG")

def main():
    total = 0
    for root, dirs, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.lower().endswith('.png'):
                total += 1
    print(f"找到 {total} 个 PNG 文件，开始处理...")
    count = 0
    for root, dirs, files in os.walk(INPUT_DIR):
        for fname in files:
            if fname.lower().endswith('.png'):
                src = os.path.join(root, fname)
                rel_path = os.path.relpath(src, INPUT_DIR)
                dst = os.path.join(OUTPUT_DIR, rel_path)
                try:
                    process_file(src, dst)
                    count += 1
                    print(f"[{count}/{total}] {rel_path} 完成")
                except Exception as e:
                    print(f"[{count}/{total}] {rel_path} 失败: {e}")

if __name__ == "__main__":
    main()