import os
import random
import shutil

# ================= 配置区域 =================
# 1. 你现在存放大批量图片的文件夹
SOURCE_DIR = r"F:\cattle2\train_merged_all"

# 2. 你想把挑出来的100张图放到哪里 (用于人工标注)
# 程序会自动创建这个文件夹
TARGET_DIR = r"F:\cattle2\to_label_100"

# 3. 抽取数量
PICK_NUM = 100
# ===========================================

def move_random_images():
    # 检查源文件夹是否存在
    if not os.path.exists(SOURCE_DIR):
        print(f"错误：找不到源文件夹 {SOURCE_DIR}")
        return

    # 创建目标文件夹
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"已创建目标文件夹: {TARGET_DIR}")

    # 1. 扫描所有图片
    print("正在扫描图片...")
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    all_images = []
    
    for f in os.listdir(SOURCE_DIR):
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            all_images.append(f)

    total_count = len(all_images)
    print(f"源文件夹共有 {total_count} 张图片。")

    if total_count < PICK_NUM:
        print(f"警告：图片总数 ({total_count}) 少于你要抽取的数量 ({PICK_NUM})！")
        print("将移动所有图片。")
        selected_images = all_images
    else:
        # 2. 核心步骤：随机打乱并抽取
        print(f"正在随机抽取 {PICK_NUM} 张...")
        selected_images = random.sample(all_images, PICK_NUM)

    # 3. 执行移动操作
    count = 0
    for image_name in selected_images:
        src_path = os.path.join(SOURCE_DIR, image_name)
        dst_path = os.path.join(TARGET_DIR, image_name)

        try:
            # 使用 move (剪切)，这样原来的文件夹里剩下的就是未标注的，方便后续管理
            # 如果你只想复制，把 shutil.move 改成 shutil.copy2
            shutil.move(src_path, dst_path)
            count += 1
        except Exception as e:
            print(f"移动失败 {image_name}: {e}")

    print("-" * 30)
    print(f"成功！已随机抽取并移动了 {count} 张图片。")
    print(f"请打开 LabelImg，并在左侧点击 'Open Dir' 选择这个文件夹：")
    print(f"👉 {TARGET_DIR}")

if __name__ == '__main__':
    move_random_images()