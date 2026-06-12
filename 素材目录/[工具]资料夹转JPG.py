import sys
import os
from PIL import Image

def process_image(input_path, output_path):
    """轉換單一圖片為 Baseline JPG"""
    try:
        with Image.open(input_path) as img:
            # JPG 不支援 Alpha，轉為白色背景
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if 'A' in img.getbands() else None)
                img_rgb = background
            else:
                img_rgb = img.convert("RGB")

            # 確保目標目錄存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 儲存為 Baseline JPEG
            img_rgb.save(output_path, "JPEG", quality=60, progressive=False, optimize=True)
            print(f"✅ 已轉換: {output_path}")
    except Exception as e:
        print(f"❌ 處理失敗 {input_path}: {e}")

def walk_directory(input_dir, output_dir):
    """遞迴掃描目錄並執行轉換"""
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.bmp', '.gif')):
                # 建構完整路徑
                src_path = os.path.join(root, file)
                
                # 計算相對路徑以維持結構
                rel_path = os.path.relpath(src_path, input_dir)
                dest_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + ".png")
                
                process_image(src_path, dest_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python toJPG.py <輸入目錄> <輸出目錄>")
    else:
        walk_directory(sys.argv[1], sys.argv[2])