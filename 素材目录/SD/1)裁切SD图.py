import os
from PIL import Image
from glob import glob

# ================= 配置 =================
INPUT_DIR = r".\SD"
OUTPUT_DIR = r".\SD裁切"
TARGET_WIDTH = 192   # 目标宽度（像素）
# ========================================

def resize_image(src_path, dst_path):
    """将图片等比缩放到目标宽度，保存到目标路径"""
    with Image.open(src_path) as img:
        # 计算目标高度（保持宽高比）
        w, h = img.size
        new_h = int(h * TARGET_WIDTH / w)
        # 缩放使用高质量重采样滤镜
        img_resized = img.resize((TARGET_WIDTH, new_h), Image.LANCZOS)
        # 保存前确保目标目录存在
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        img_resized.save(dst_path, "PNG")

def main():
    # 递归获取所有 PNG 文件（包括子目录）
    pattern = os.path.join(INPUT_DIR, "**", "*.png")
    all_pngs = glob(pattern, recursive=True)
    total = len(all_pngs)
    print(f"找到 {total} 个 PNG 文件，开始处理...")

    for idx, src_path in enumerate(all_pngs, 1):
        # 计算输出路径（保持相对目录结构）
        rel_path = os.path.relpath(src_path, INPUT_DIR)
        dst_path = os.path.join(OUTPUT_DIR, rel_path)
        try:
            resize_image(src_path, dst_path)
            print(f"[{idx}/{total}] 完成: {rel_path}")
        except Exception as e:
            print(f"[{idx}/{total}] 失败: {rel_path} - {e}")

    print("全部处理完毕！")

if __name__ == "__main__":
    main()