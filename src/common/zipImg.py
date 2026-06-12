import os
import subprocess

# 配置 pngquant.exe 的絕對路徑（注意：Windows 下最好加上 .exe 擴充檔名）
PNGQUANT_PATH = r'C:\Users\user\Downloads\Compressed\pngquant-windows\pngquant\pngquant.exe'

def compress_png(filepath):
    orig_size = os.path.getsize(filepath)
    if orig_size == 0:
        return 0, 0, False, "空檔案"

    try:
        # 直接呼叫 pngquant 命令行
        # --force: 強制覆蓋原檔
        # --ext .png: 輸出副檔名保持 .png
        # --quality=65-80: 圖片品質區間
        # --speed 3: 壓縮速度（1最慢最好，11最快，3是平衡點）
        cmd = [
            PNGQUANT_PATH,
            '--force',
            '--ext', '.png',
            '--quality=40-60',
            '--speed', '1',
            filepath
        ]
        
        # 執行並捕獲錯誤
        result = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
        
        # pngquant 狀態碼说明：
        # 0 = 成功
        # 98 = 壓縮後體積變大（自動忽略並保留原檔）
        # 其他 = 錯誤
        
        if result.returncode == 0:
            new_size = os.path.getsize(filepath)
            if new_size < orig_size:
                return orig_size, new_size, True, None
            else:
                return orig_size, orig_size, False, "壓縮後未變小"
        elif result.returncode == 98:
            return orig_size, orig_size, False, "防膨脹（跳過）"
        else:
            return orig_size, orig_size, False, f"錯誤: {result.stderr.strip()}"
            
    except Exception as e:
        return orig_size, orig_size, False, str(e)


def main():
    root_dir = os.getcwd()
    print(f"遞迴壓縮目錄: {root_dir}")

    total_files = 0
    total_replaced = 0
    total_orig_bytes = 0
    total_new_bytes = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.png'):
                filepath = os.path.join(dirpath, fname)
                orig, new, replaced, err = compress_png(filepath)

                total_files += 1
                total_orig_bytes += orig
                # 修正 Bug：不論有無替換，都加上實際的最終大小
                total_new_bytes += new 

                if replaced:
                    total_replaced += 1
                    saved = orig - new
                    percent = (saved / orig) * 100 if orig else 0
                    print(f"✓ {os.path.relpath(filepath, root_dir)}  {orig/1024:.1f}KB → {new/1024:.1f}KB  ({percent:.1f}% 減小)")
                else:
                    print(f"✗ {os.path.relpath(filepath, root_dir)}  {orig/1024:.1f}KB  {err or '保留原文件'}")

    print("\n=== 統計 ===")
    print(f"處理文件總數: {total_files}")
    print(f"成功壓縮並替換: {total_replaced}")
    print(f"跳過 (防膨脹/錯誤): {total_files - total_replaced}")
    if total_orig_bytes:
        overall_saved = total_orig_bytes - total_new_bytes
        print(f"原始總大小: {total_orig_bytes/1024:.1f} KB")
        print(f"壓縮後總大小: {total_new_bytes/1024:.1f} KB")
        print(f"整體節省: {overall_saved/1024:.1f} KB ({overall_saved/total_orig_bytes*100:.1f}%)")


if __name__ == '__main__':
    main()
