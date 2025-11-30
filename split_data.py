import os
import shutil
import random
from tqdm import tqdm

# ================= 🔧 配置区域 =================

# 1. 源文件夹
source_folder = r"F:\cattle_train\train_shuffled_final"

# 2. 目标文件夹
target_folder = r"F:\cattle_train\YOLO_Dataset_Formatted_WithTest"

# 3. 划分比例 (和必须为 1.0)
train_ratio = 0.8  # 80% 训练
val_ratio = 0.1  # 10% 验证
test_ratio = 0.1  # 10% 测试 (完全独立的考试题)

# 4. 是否随机打乱 (True=随机, False=按文件名顺序)
# 如果是视频连续帧，建议选 False 以避免数据泄露；如果是散图选 True。
random_split = True

# 5. 模式: 'move' (移动) 或 'copy' (复制)
action_mode = 'move'


# ===============================================

def split_dataset():
    if not os.path.exists(source_folder):
        print(f"❌ 错误：找不到文件夹 {source_folder}")
        return

    # 扫描图片
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    imgs = [f for f in os.listdir(source_folder) if os.path.splitext(f)[-1].lower() in img_extensions]
    total_imgs = len(imgs)

    if total_imgs == 0:
        print("❌ 错误：没找到图片！")
        return

    print(f"✅ 找到图片共: {total_imgs} 张")

    # 打乱或排序
    if random_split:
        print("🔀 正在随机打乱...")
        random.shuffle(imgs)
    else:
        print("🔢 保持文件名顺序...")
        imgs.sort()

    # 计算数量
    train_count = int(total_imgs * train_ratio)
    val_count = int(total_imgs * val_ratio)
    # 剩下的全给测试集，保证总数对得上
    test_count = total_imgs - train_count - val_count

    # 切分列表
    train_imgs = imgs[:train_count]
    val_imgs = imgs[train_count: train_count + val_count]
    test_imgs = imgs[train_count + val_count:]

    # 创建目录
    subsets = ['train', 'val', 'test']
    for subset in subsets:
        os.makedirs(os.path.join(target_folder, 'images', subset), exist_ok=True)
        os.makedirs(os.path.join(target_folder, 'labels', subset), exist_ok=True)

    print(f"📁 目录结构已创建于: {target_folder}")

    # 移动/复制函数
    def process_files(img_list, subset_name):
        for img_name in tqdm(img_list, desc=f"处理 {subset_name} 集"):
            src_img_path = os.path.join(source_folder, img_name)

            name_no_ext = os.path.splitext(img_name)[0]
            txt_name = name_no_ext + ".txt"
            src_txt_path = os.path.join(source_folder, txt_name)

            dst_img_path = os.path.join(target_folder, 'images', subset_name, img_name)
            dst_txt_path = os.path.join(target_folder, 'labels', subset_name, txt_name)

            if action_mode == 'move':
                shutil.move(src_img_path, dst_img_path)
            else:
                shutil.copy(src_img_path, dst_img_path)

            if os.path.exists(src_txt_path):
                if action_mode == 'move':
                    shutil.move(src_txt_path, dst_txt_path)
                else:
                    shutil.copy(src_txt_path, dst_txt_path)

    # 执行
    process_files(train_imgs, 'train')
    process_files(val_imgs, 'val')
    process_files(test_imgs, 'test')

    print(f"\n🎉 全部完成！")
    print(f"训练集: {len(train_imgs)}")
    print(f"验证集: {len(val_imgs)}")
    print(f"测试集: {len(test_imgs)}")
    print(f"请在 yaml 中添加: test: images/test")


if __name__ == '__main__':
    split_dataset()