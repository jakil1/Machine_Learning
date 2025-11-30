import os
import shutil
import hashlib
from imagededup.methods import PHash

# ================= 配置区域 =================
# 你的数据集路径
WORK_DIR = r"F:\cattle3\train_merged_all"

# 存放被剔除图片的备份文件夹
BACKUP_DIR = os.path.join(WORK_DIR, "duplicates_backup")

# 相似度阈值 (0-64)
# 视频抽帧建议设为 2 或 3。
# 0代表完全一样，数值越小越严格。
# 设为 3 意味着允许非常细微的差异（比如光照微变、噪点），这对于视频帧去重很有效。
SIMILARITY_THRESHOLD = 3 
# ===========================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_md5(file_path):
    """计算文件的MD5值"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def step1_remove_exact_duplicates():
    print(">>> 第一步：正在扫描完全重复的文件 (MD5)...")
    exact_dir = os.path.join(BACKUP_DIR, "exact_copies")
    ensure_dir(exact_dir)
    
    seen_hashes = {}
    count = 0
    
    # 获取所有图片
    all_files = [f for f in os.listdir(WORK_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    for file in all_files:
        path = os.path.join(WORK_DIR, file)
        if not os.path.isfile(path): continue
        
        file_hash = get_md5(path)
        
        if file_hash in seen_hashes:
            # 发现重复，移走
            shutil.move(path, os.path.join(exact_dir, file))
            count += 1
            # print(f"移走完全重复: {file}")
        else:
            seen_hashes[file_hash] = file
            
    print(f"    [完成] 移除了 {count} 张完全一模一样的图片。\n")

def step2_remove_visual_duplicates():
    print(">>> 第二步：正在基于 AI 感知哈希 (pHash) 识别相似图片...")
    print("    (这一步需要计算每张图的指纹，图片多的话请耐心等待...)")
    
    visual_dir = os.path.join(BACKUP_DIR, "visual_similar")
    ensure_dir(visual_dir)

    phasher = PHash()
    
    # 1. 生成所有图片的编码
    # imagededup 会自动扫描目录下的图片
    encodings = phasher.encode_images(image_dir=WORK_DIR)
    
    # 2. 查找重复
    # find_duplicates 返回的是一个字典 {文件名: [重复文件列表]}
    duplicates = phasher.find_duplicates(encoding_map=encodings, max_distance_threshold=SIMILARITY_THRESHOLD)
    
    count = 0
    processed_files = set() # 记录已经处理过的文件，防止重复操作

    # 3. 处理重复列表
    # 这种方法会保留列表中的“键”(Key)，移走“值”(Value)里面的文件
    # 比如 {'A.jpg': ['B.jpg', 'C.jpg']} -> 保留 A，移走 B 和 C
    
    # 对文件名排序，保证每次运行结果一致（优先保留名字靠前的）
    sorted_filenames = sorted(duplicates.keys())
    
    for filename in sorted_filenames:
        # 如果这个文件之前被当作别人的重复项移走了，就跳过
        if filename in processed_files:
            continue
            
        dup_list = duplicates[filename]
        
        if dup_list:
            for dup_file in dup_list:
                # 构建路径
                src = os.path.join(WORK_DIR, dup_file)
                dst = os.path.join(visual_dir, dup_file)
                
                if os.path.exists(src):
                    try:
                        shutil.move(src, dst)
                        processed_files.add(dup_file) # 标记这个文件已经被处理（移走）了
                        count += 1
                        print(f"移走相似图: {dup_file} (与 {filename} 极度相似)")
                    except Exception as e:
                        print(f"移动失败: {dup_file} Error: {e}")

    print(f"    [完成] 移除了 {count} 张视觉上高度重复的图片。")

if __name__ == '__main__':
    print(f"目标处理路径: {WORK_DIR}")
    print("-" * 40)
    
    step1_remove_exact_duplicates()
    step2_remove_visual_duplicates()
    
    print("-" * 40)
    print("所有去重工作完成！")
    print(f"重复的图片都保存在这里了，请去检查一下: {BACKUP_DIR}")
    print("确认没问题后，可以直接删除 duplicates_backup 文件夹。")