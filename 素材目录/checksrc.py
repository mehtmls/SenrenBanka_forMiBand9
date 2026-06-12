import os
import json
import glob
import re
from pathlib import Path

def extract_referenced_images(txt_dir):
    """
    遍历所有 .txt 脚本文件，提取：
    1. Img 字段 -> 转换为实际图片路径（立绘/表情/SD）
    2. background 字段 -> 直接作为背景图片路径（相对 common 目录）
    返回一个集合，包含所有引用的图片相对路径（使用正斜杠）。
    """
    img_paths = set()
    txt_files = glob.glob(os.path.join(txt_dir, "*.txt"))
    
    for txt_path in txt_files:
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def traverse(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == 'Img' and isinstance(v, str):
                            # 处理 Img 字段（立绘/表情/SD）
                            img_paths.update(convert_img_value(v))
                        elif k == 'background' and isinstance(v, str):
                            # 处理 background 字段（背景图片）
                            if v:  # 非空
                                img_paths.add(f"{v}.png")
                        else:
                            traverse(v)
                elif isinstance(obj, list):
                    for item in obj:
                        traverse(item)
            
            traverse(data)
        except Exception as e:
            print(f"读取 {txt_path} 时出错: {e}")
    
    return img_paths

def convert_img_value(val):
    """将 Img 字段值转换为实际的图片路径列表"""
    results = set()
    if not val:
        return results
    
    # 角色名修正映射（根据实际目录调整）
    ROLE_MAP = {
        "白狛": "白狗",   # 实际目录为 face白狗a
        # 其他不一致可添加
    }
    
    if val.startswith("sd"):
        # SD 图片：尝试原样和全大写两种形式
        results.add(f"sd/{val}.png")
        results.add(f"sd/{val.upper()}.png")
    else:
        # 普通立绘格式: 角色_face编号_服装名
        parts = val.split('_')
        if len(parts) >= 3:
            role_raw = parts[0]
            role = ROLE_MAP.get(role_raw, role_raw)  # 应用角色名映射
            face_code = parts[1][4:]  # 去掉 'face' 前缀
            dress_name = parts[2]
            results.add(f"assets/{role}a/dress/{dress_name}.png")
            results.add(f"assets/{role}a/face/{face_code}.png")
        else:
            # 不符合预期格式，直接加 .png 尝试
            results.add(f"{val}.png")
    return results

def scan_actual_pngs(common_dir):
    """扫描 common 目录下所有 .png 文件，返回相对路径集合"""
    common_path = Path(common_dir)
    png_files = set()
    for png_path in common_path.rglob("*.png"):
        rel_path = png_path.relative_to(common_path).as_posix()
        png_files.add(rel_path)
    return png_files

def main():
    script_txt_dir = "./5"                     # 存放处理后的 .txt 文件的目录
    common_dir = "G:/project/SenrenBanka/src/common"   # 游戏 common 目录
    
    if not os.path.isdir(common_dir):
        print(f"错误：目录 {common_dir} 不存在")
        return
    
    print("正在提取脚本中引用的图片（包括 Img 和 Background）...")
    referenced = extract_referenced_images(script_txt_dir)
    print(f"共找到 {len(referenced)} 个引用（含重复）")
    
    print("正在扫描 common 目录下的实际 PNG 文件...")
    actual = scan_actual_pngs(common_dir)
    print(f"实际共有 {len(actual)} 个 PNG 文件")
    
    missing = referenced - actual
    extra = actual - referenced
    
    print("\n========== 缺失的图片（脚本需要但实际缺失） ==========")
    if missing:
        for m in sorted(missing):
            print(m)
        print(f"\n总计缺失 {len(missing)} 个")
    else:
        print("无缺失")
    
    print("\n========== 多余的图片（实际存在但脚本未引用） ==========")
    if extra:
        # 可以过滤掉 UI 等非脚本直接引用的文件（按需）
        # 这里简单列出全部
        for e in sorted(extra):
            print(e)
        print(f"\n总计多余 {len(extra)} 个")
    else:
        print("无多余")

if __name__ == "__main__":
    main()