import os
from PIL import Image, ImageOps

# ===== 配置区 =====
SCREEN_DIR = r".\BG"          # 背景图片所在文件夹
TARGET_WIDTH = 300            # 目标宽度（像素）
TARGET_HEIGHT = 490           # 目标高度（像素）
OVERWRITE = False             # True=覆盖原文件，False=输出到同级目录下的 {文件夹名}_resized
# ==================

def resize_images(folder, target_w, target_h, overwrite):
    """缩放文件夹内所有 PNG 图片到目标尺寸（居中裁切）"""
    if not os.path.isdir(folder):
        print(f"文件夹不存在：{folder}")
        return

    if overwrite:
        out_dir = folder
    else:
        # 获取父目录和原文件夹名
        parent_dir = os.path.dirname(folder.rstrip(os.sep))
        base_name = os.path.basename(folder.rstrip(os.sep))
        new_dir_name = f"{base_name}_resized"
        out_dir = os.path.join(parent_dir, new_dir_name)
        os.makedirs(out_dir, exist_ok=True)

    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
    total = len(files)
    if total == 0:
        print("没有找到 PNG 文件")
        return

    print(f"开始处理 {total} 张图片 -> 目标尺寸 {target_w}x{target_h}")
    print(f"输出目录：{out_dir}")

    for i, fname in enumerate(files, 1):
        in_path = os.path.join(folder, fname)
        try:
            img = Image.open(in_path).convert("RGBA")
            # 居中裁切并缩放到目标尺寸
            resized_cropped = ImageOps.fit(
                img,
                (target_w, target_h),
                method=Image.LANCZOS,
                centering=(0.5, 0.5)
            )
            out_path = os.path.join(out_dir, fname)
            resized_cropped.save(out_path, "PNG")
            print(f"[{i}/{total}] {fname} 已完成")
        except Exception as e:
            print(f"[{i}/{total}] {fname} 失败: {e}")

    print("全部处理完成！")

if __name__ == "__main__":
    resize_images(SCREEN_DIR, TARGET_WIDTH, TARGET_HEIGHT, OVERWRITE)