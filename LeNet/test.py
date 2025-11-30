import os
import random
import shutil
from sklearn.model_selection import train_test_split


def get_image_label_pairs(image_dirs, label_dirs):
    """
    获取图像和对应标签文件的配对
    """
    pairs = []

    for image_dir, label_dir in zip(image_dirs, label_dirs):
        # 检查目录是否存在
        if not os.path.exists(image_dir):
            print(f"警告: 图像目录不存在 {image_dir}")
            continue
        if not os.path.exists(label_dir):
            print(f"警告: 标签目录不存在 {label_dir}")
            continue

        for img_file in os.listdir(image_dir):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                img_path = os.path.join(image_dir, img_file)

                # 构建对应的标签文件路径
                label_file = os.path.splitext(img_file)[0] + '.txt'
                label_path = os.path.join(label_dir, label_file)

                # 检查标签文件是否存在
                if os.path.exists(label_path):
                    pairs.append((img_path, label_path))
                else:
                    print(f"警告: 找不到标签文件 {label_path}，跳过图像 {img_path}")

    return pairs


def create_directories(base_path):
    """创建新的目录结构"""
    directories = [
        os.path.join(base_path, 'images', 'train'),
        os.path.join(base_path, 'images', 'val'),
        os.path.join(base_path, 'images', 'test'),
        os.path.join(base_path, 'labels', 'train'),
        os.path.join(base_path, 'labels', 'val'),
        os.path.join(base_path, 'labels', 'test')
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"创建目录: {directory}")


def copy_yolo_pairs(pairs, split_name, new_base_path):
    """复制图像和标签文件对到新位置"""
    copied_count = 0
    for img_path, label_path in pairs:
        try:
            # 新路径
            img_filename = os.path.basename(img_path)
            label_filename = os.path.basename(label_path)

            new_img_path = os.path.join(new_base_path, 'images', split_name, img_filename)
            new_label_path = os.path.join(new_base_path, 'labels', split_name, label_filename)

            # 复制文件
            shutil.copy2(img_path, new_img_path)
            shutil.copy2(label_path, new_label_path)
            copied_count += 1
        except Exception as e:
            print(f"错误: 复制文件时出错 {img_path} -> {e}")

    print(f"成功复制 {copied_count} 个文件到 {split_name} 集合")


def verify_split(new_base_path):
    """验证每个集合的样本数量"""
    splits = ['train', 'val', 'test']
    for split in splits:
        img_dir = os.path.join(new_base_path, 'images', split)
        label_dir = os.path.join(new_base_path, 'labels', split)

        if not os.path.exists(img_dir) or not os.path.exists(label_dir):
            print(f"错误: {split} 集合目录不存在")
            continue

        img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        label_files = [f for f in os.listdir(label_dir) if f.endswith('.txt')]

        img_count = len(img_files)
        label_count = len(label_files)

        print(f"{split}: {img_count} 图像, {label_count} 标签")

        # 检查图像和标签是否匹配
        if img_count != label_count:
            print(f"警告: {split}集合中图像和标签数量不匹配!")

        # 检查是否有对应的标签文件
        missing_labels = 0
        for img_file in img_files:
            label_file = os.path.splitext(img_file)[0] + '.txt'
            if label_file not in label_files:
                missing_labels += 1
                print(f"警告: 图像 {img_file} 没有对应的标签文件")

        if missing_labels > 0:
            print(f"警告: {split}集合中有 {missing_labels} 个图像没有对应的标签文件")


def create_data_yaml(new_base_path, class_names, train_path, val_path, test_path):
    """创建YOLO格式的data.yaml文件"""
    yaml_content = f"""# YOLO数据集配置文件
train: {train_path}
val: {val_path}
test: {test_path}

nc: {len(class_names)}
names: {class_names}
"""

    yaml_path = os.path.join(new_base_path, 'data.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"创建data.yaml文件: {yaml_path}")


def main():
    # ==============================
    # 需要替换的路径部分 - 开始
    # ==============================

    # 原始数据集根路径（images目录的上一级）
    original_dataset_root = "F:/Trackdata"  # 替换为你的原始数据集根路径

    # 新数据集根路径（images目录的上一级）
    new_dataset_root = "F:/Trackdata2"  # 替换为你想要创建的新数据集根路径

    # 类别名称列表
    class_names = ['calf','cattle']  # 替换为你的实际类别名称

    # ==============================
    # 需要替换的路径部分 - 结束
    # ==============================

    # 基于根路径构建完整的图像和标签路径
    original_train_images = os.path.join(original_dataset_root, 'images', 'train')
    original_train_labels = os.path.join(original_dataset_root, 'labels', 'train')
    original_val_images = os.path.join(original_dataset_root, 'images', 'val')
    original_val_labels = os.path.join(original_dataset_root, 'labels', 'val')

    print("开始获取图像-标签对...")
    # 获取训练集和验证集的所有图像-标签对
    train_pairs = get_image_label_pairs([original_train_images], [original_train_labels])
    val_pairs = get_image_label_pairs([original_val_images], [original_val_labels])

    all_pairs = train_pairs + val_pairs
    print(f"总共找到 {len(all_pairs)} 个有效的图像-标签对")

    if len(all_pairs) == 0:
        print("错误: 没有找到任何有效的图像-标签对，请检查路径设置")
        return

    # 重新划分数据集
    print("开始重新划分数据集...")
    train_val_pairs, test_pairs = train_test_split(
        all_pairs, test_size=0.2, random_state=42
    )
    train_pairs, val_pairs = train_test_split(
        train_val_pairs, test_size=0.25, random_state=42  # 0.25 * 0.8 = 0.2
    )

    print(f"新训练集: {len(train_pairs)} 对")
    print(f"新验证集: {len(val_pairs)} 对")
    print(f"新测试集: {len(test_pairs)} 对")

    # 创建新目录结构
    print("创建新目录结构...")
    create_directories(new_dataset_root)

    # 复制文件到新位置
    print("复制文件到新位置...")
    copy_yolo_pairs(train_pairs, 'train', new_dataset_root)
    copy_yolo_pairs(val_pairs, 'val', new_dataset_root)
    copy_yolo_pairs(test_pairs, 'test', new_dataset_root)

    # 验证划分结果
    print("验证划分结果...")
    verify_split(new_dataset_root)

    # 创建data.yaml文件
    print("创建data.yaml文件...")
    create_data_yaml(
        new_dataset_root,
        class_names,
        train_path='./images/train',
        val_path='./images/val',
        test_path='./images/test'
    )

    print("数据集重新划分完成!")


if __name__ == "__main__":
    main()