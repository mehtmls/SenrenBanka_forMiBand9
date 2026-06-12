import sys
import os
import shutil
from PIL import Image

def merge_similar_colors(colors_list, tolerance=5, has_alpha=False):
    """將 RGB 誤差在 +-5 以內的相似顏色合併"""
    sorted_colors = sorted(colors_list, key=lambda x: x, reverse=True)
    merged_mapping = {}
    unique_centers = []
    
    for count, color_tuple in sorted_colors:
        found_match = False
        if has_alpha:
            r, g, b, a = color_tuple
            for cr, cg, cb, ca in unique_centers:
                if a == ca and abs(r - cr) <= tolerance and abs(g - cg) <= tolerance and abs(b - cb) <= tolerance:
                    merged_mapping[color_tuple] = (cr, cg, cb, ca)
                    found_match = True
                    break
        else:
            r, g, b = color_tuple
            for cr, cg, cb in unique_centers:
                if abs(r - cr) <= tolerance and abs(g - cg) <= tolerance and abs(b - cb) <= tolerance:
                    merged_mapping[color_tuple] = (cr, cg, cb)
                    found_match = True
                    break
        if not found_match:
            unique_centers.append(color_tuple)
            merged_mapping[color_tuple] = color_tuple
    return merged_mapping, len(unique_centers)


def main():
    if len(sys.argv) < 3:
        print("錯誤: 參數不足！")
        print("使用方法: python conv.py <輸入圖片路徑> <輸出圖片路徑>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(input_path):
        print(f"錯誤: 找不到輸入檔案 '{input_path}'")
        sys.exit(1)
        
    orig_file_size = os.path.getsize(input_path)
    temp_output_path = output_path + ".tmp.png"
        
    img_orig = Image.open(input_path)
    has_alpha = img_orig.mode in ('RGBA', 'LA') or (img_orig.mode == 'P' and 'transparency' in img_orig.info)
    
    target_mode = "RGBA" if has_alpha else "RGB"
    img_work = img_orig.convert(target_mode)
    width, height = img_work.size
    
    raw_colors = img_work.getcolors(maxcolors=width * height)
    
    # 图片过于复杂，无法获取所有颜色时，直接量化到 256 色索引
    if raw_colors is None:
        print("圖片過於複雜，直接量化到 256 色索引...")
        if has_alpha:
            img_to_save = img_work.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        else:
            img_to_save = img_work.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        img_to_save.save(temp_output_path, format="PNG", compress_level=5)
        check_and_finalize(orig_file_size, temp_output_path, output_path, input_path)
        return

    colors_list = [(count, color) for count, color in raw_colors]
    merged_mapping, final_color_count = merge_similar_colors(colors_list, tolerance=5, has_alpha=has_alpha)
    print(f"原始顏色數: {len(colors_list)} 色 -> 經 RGB±5 合併後剩餘: {final_color_count} 色")
    
    # 修改：将调色板模式的阈值从 32 提升到 256，大幅增加索引色使用几率
    if final_color_count <= 256:
        print(f"-> 符合條件（顏色 <= 256 色）：重構像素並切換為【調色盤模式 (PLTE)】")
        img_pixels = img_work.load()
        new_img = Image.new(target_mode, (width, height))
        new_pixels = new_img.load()
        
        for y in range(height):
            for x in range(width):
                orig_color = img_pixels[x, y]
                new_pixels[x, y] = merged_mapping.get(orig_color, orig_color)
        
        img_to_save = new_img.convert("P", palette=Image.Palette.ADAPTIVE)
    else:
        print("-> 顏色超過 256 色，自動量化至 256 色索引...")
        if has_alpha:
            img_to_save = img_work.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        else:
            img_to_save = img_work.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    img_to_save.save(temp_output_path, format="PNG", compress_level=5)
    check_and_finalize(orig_file_size, temp_output_path, output_path, input_path)


def check_and_finalize(orig_size, temp_path, final_path, orig_path):
    new_size = os.path.getsize(temp_path)
    
    print("-" * 40)
    print(f" 原始檔案大小:  {orig_size / 1024:.2f} KB")
    print(f" 優化後新大小:  {new_size / 1024:.2f} KB")
    
    if new_size >= orig_size:
        print("⚠️ 警告：優化後的檔案反而膨脹或無效益！")
        print("💡 啟動防爆保護：放棄新編碼，自動拷貝原檔作為輸出。")
        if os.path.abspath(orig_path) != os.path.abspath(final_path):
            shutil.copy2(orig_path, final_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(" 狀態：已安全還原為原檔。")
    else:
        if os.path.exists(final_path) and os.path.abspath(temp_path) != os.path.abspath(final_path):
            try:
                os.remove(final_path)
            except:
                pass
        os.rename(temp_path, final_path)
        saved_kb = (orig_size - new_size) / 1024
        saved_percent = ((orig_size - new_size) / orig_size) * 100
        print(f"🎉 成功省下容量: {saved_kb:.2f} KB ({saved_percent:.1f}%)")
    print("-" * 40)


if __name__ == "__main__":
    main()