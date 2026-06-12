import os
from PIL import Image

def rotate_and_fit_with_black_border(img, target_size):
    """
    将图片向左旋转 90 度，然后等比例缩放并填充黑边至目标尺寸 (宽, 高)，不裁剪。
    """
    target_w, target_h = target_size

    # 1. 向左旋转 90 度（逆时针）
    rotated = img.rotate(90, expand=True)

    # 2. 确保图片模式为 RGB（避免透明通道影响黑边填充）
    if rotated.mode != 'RGB':
        rotated = rotated.convert('RGB')

    # 3. 计算等比例缩放比例（使图片完整放入目标框内）
    orig_w, orig_h = rotated.size
    ratio = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * ratio)
    new_h = int(orig_h * ratio)

    # 4. 缩放图片
    img_resized = rotated.resize((new_w, new_h), Image.LANCZOS)

    # 5. 创建黑色背景图片（目标尺寸）
    black_bg = Image.new('RGB', (target_w, target_h), (0, 0, 0))

    # 6. 计算居中粘贴位置
    left = (target_w - new_w) // 2
    top = (target_h - new_h) // 2
    black_bg.paste(img_resized, (left, top))

    return black_bg

def main():
    target_dir = r".\EV合并"
    target_size = (192, 490)

    # 确保目录存在
    if not os.path.isdir(target_dir):
        print(f"目录不存在: {target_dir}")
        return

    # 遍历目录下的 .png 文件
    for filename in os.listdir(target_dir):
        if not filename.lower().endswith('.png'):
            continue

        filepath = os.path.join(target_dir, filename)
        try:
            with Image.open(filepath) as img:
                # 处理图片：旋转 + 填充黑边
                processed = rotate_and_fit_with_black_border(img, target_size)

                # 原地替换：直接保存到原路径（格式为 PNG）
                processed.save(filepath, format='PNG')
                print(f"已处理: {filename}")
        except Exception as e:
            print(f"处理失败 {filename}: {e}")

if __name__ == "__main__":
    main()