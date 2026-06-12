import os
import shutil
import re

# 设置基础目录（char_layers 所在路径）
base_dir = r".\立绘裁切"

# 要复制的后缀模式（正则表达式）
# 匹配以 ntr(误) 结尾的文件名（如 06n.png, 18r.png），也包含 m、d 等可根据需要添加
# 根据之前缺失列表，我们重点关注 ntr(误)
PATTERN = re.compile(r'^(\d+)([ntr])\.png$', re.IGNORECASE)

def find_role_pairs(base_path):
    """找出所有带有 a 和 b 后缀的角色对"""
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    role_names = set()
    for d in dirs:
        # 匹配 角色名a 或 角色名b
        m = re.match(r'^(.+?)([ab])$', d)
        if m:
            role_names.add(m.group(1))
    pairs = []
    for role in role_names:
        a_dir = os.path.join(base_path, role + 'a')
        b_dir = os.path.join(base_path, role + 'b')
        if os.path.isdir(a_dir) and os.path.isdir(b_dir):
            pairs.append((role, a_dir, b_dir))
    return pairs

def copy_missing_files(role, a_face_dir, b_face_dir):
    """从 b/face 复制缺失的符合模式的文件到 a/face"""
    a_face_path = os.path.join(a_face_dir, 'face')
    b_face_path = os.path.join(b_face_dir, 'face')
    
    if not os.path.isdir(a_face_path) or not os.path.isdir(b_face_path):
        print(f"  [跳过] {role}: face 目录不存在")
        return []
    
    copied = []
    for fname in os.listdir(b_face_path):
        if not fname.endswith('.png'):
            continue
        # 检查是否符合后缀模式（n/t/r）
        match = PATTERN.match(fname)
        if not match:
            continue
        # 检查 a 中是否存在
        src = os.path.join(b_face_path, fname)
        dst = os.path.join(a_face_path, fname)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            copied.append(fname)
            print(f"  [复制] {fname} -> {dst}")
    return copied

def main():
    if not os.path.isdir(base_dir):
        print(f"错误: 目录 {base_dir} 不存在")
        return
    
    pairs = find_role_pairs(base_dir)
    if not pairs:
        print("未找到任何 a/b 角色对。")
        return
    
    print(f"找到 {len(pairs)} 个角色对:\n")
    all_copied = {}
    for role, a_dir, b_dir in pairs:
        print(f"处理角色: {role}")
        a_face = os.path.join(a_dir, 'face')
        if not os.path.isdir(a_face):
            print(f"  警告: {a_face} 不存在，跳过")
            continue
        copied = copy_missing_files(role, a_dir, b_dir)
        if copied:
            all_copied[role] = copied
        print()
    
    if all_copied:
        print("\n已完成所有缺失文件的复制。")
    else:
        print("\n没有需要复制的文件。")

if __name__ == "__main__":
    main()