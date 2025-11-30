import os
import random
import shutil
from tqdm import tqdm  # 如果没有这个库，可以去掉这行和下面的 tqdm

# ================= 配置区域 =================
# 1. 你的原始图片文件夹 (乱序、名字乱七八糟的)
SOURCE_DIR = r"F:\cattle3\train_merged_all"

# 2. 打乱后存放的新文件夹
TARGET_DIR = r"F:\cattle3\train_shuffled_final"

# 3. 重命名的前缀 (可选)
# 如果填 "", 文件名就是 000001.jpg
# 如果填 "cattle_", 文件名就是 cattle_000001.jpg
PREFIX = "cattle" 
# ===========================================

def shuffle_and_rename():
    # 1. 检查路径
    if not os.path.exists(SOURCE_DIR):
        print("找不到源文件夹！")
        return
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    # 2. 获取所有图片
    print("正在读取图片列表...")
    valid_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    images = [f for f in os.listdir(SOURCE_DIR) if os.path.splitext(f)[1].lower() in valid_exts]
    
    total_num = len(images)
    print(f"共找到 {total_num} 张图片。")

    # 3. 【关键步骤】随机打乱
    print("正在洗牌 (Shuffling)...")
    random.shuffle(images)

    # 4. 复制并重命名
    print("正在复制并重命名...")
    
    # 使用 tqdm 显示进度条 (如果没有装 tqdm，就把 range(total_num) 放进循环里)
    # 也就是: for i, filename in enumerate(images):
    for i, filename in enumerate(tqdm(images)):
        # 获取原文件后缀 (.jpg)
        ext = os.path.splitext(filename)[1].lower()
        
        # 构造新名字: 000001.jpg (6位数字，不够补零)
        new_name = f"{PREFIX}{i+1:06d}{ext}"
        
        src_path = os.path.join(SOURCE_DIR, filename)
        dst_path = os.path.join(TARGET_DIR, new_name)
        
        # 复制文件 (使用 copy2 保留文件时间戳等信息)
        shutil.copy2(src_path, dst_path)

    print("-" * 30)
    print("完成！")
    print(f"打乱后的图片已保存在: {TARGET_DIR}")
    print("原来的文件夹没动，确认新文件夹没问题后可以手动删除旧的。")

if __name__ == '__main__':
    # 如果报错 No module named 'tqdm'，请在终端 pip install tqdm
    # 或者删掉代码里的 tqdm 相关部分
    shuffle_and_rename()