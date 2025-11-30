import hashlib
import os
from PIL import Image
import numpy as np


def calculate_image_hash(image_path, hash_size=8):
    """计算图像的感知哈希"""
    try:
        image = Image.open(image_path)
        # 转换为灰度图并调整大小
        image = image.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
        pixels = np.array(image)
        # 计算平均值并生成哈希
        avg = pixels.mean()
        hash_value = 0
        for i in range(hash_size):
            for j in range(hash_size):
                if pixels[i, j] > avg:
                    hash_value |= 1 << (i * hash_size + j)
        return hash_value
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def check_dataset_overlap(train_dir, test_dir):
    """检查训练集和测试集是否有重叠"""
    train_hashes = {}
    test_hashes = {}

    print("Calculating hashes for training images...")
    train_count = 0
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                img_hash = calculate_image_hash(path)
                if img_hash is not None:
                    train_hashes[img_hash] = path
                train_count += 1
                if train_count % 100 == 0:
                    print(f"Processed {train_count} training images...")

    print("Calculating hashes for test images...")
    test_count = 0
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                img_hash = calculate_image_hash(path)
                if img_hash is not None:
                    test_hashes[img_hash] = path
                test_count += 1
                if test_count % 100 == 0:
                    print(f"Processed {test_count} test images...")

    # 查找重叠
    train_hash_set = set(train_hashes.keys())
    test_hash_set = set(test_hashes.keys())
    overlap_hashes = train_hash_set.intersection(test_hash_set)

    print(f"\n=== Overlap Analysis ===")
    print(f"Training images processed: {len(train_hashes)}")
    print(f"Test images processed: {len(test_hashes)}")
    print(f"Overlapping images: {len(overlap_hashes)}")

    if overlap_hashes:
        print("\nOverlapping images found:")
        for i, hash_val in enumerate(list(overlap_hashes)):
            if i >= 10:  # 只显示前10个重叠
                print(f"... and {len(overlap_hashes) - 10} more overlapping images")
                break
            print(f"Hash: {hash_val}")
            print(f"Train: {train_hashes[hash_val]}")
            print(f"Test:  {test_hashes[hash_val]}")
            print("---")

        # 保存重叠文件列表到文本文件
        with open("overlapping_images.txt", "w") as f:
            f.write("Overlapping images between train and val sets:\n")
            f.write("=" * 50 + "\n")
            for hash_val in overlap_hashes:
                f.write(f"Train: {train_hashes[hash_val]}\n")
                f.write(f"Val:   {test_hashes[hash_val]}\n")
                f.write("-" * 30 + "\n")
        print(f"\nOverlapping images list saved to: overlapping_images.txt")
    else:
        print("✅ No overlapping images found!")

    return len(overlap_hashes) > 0, overlap_hashes


def check_filename_overlap(train_dir, test_dir):
    """通过文件名检查数据集重叠"""
    train_files = set()
    test_files = set()

    print("Collecting training filenames...")
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                train_files.add(file.lower())

    print("Collecting test filenames...")
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_files.add(file.lower())

    # 查找重叠
    overlap_files = train_files.intersection(test_files)

    print(f"\n=== Filename Overlap Analysis ===")
    print(f"Training files: {len(train_files)}")
    print(f"Test files: {len(test_files)}")
    print(f"Overlapping files: {len(overlap_files)}")

    if overlap_files:
        print("\nOverlapping filenames:")
        for i, file in enumerate(list(overlap_files)):
            if i >= 20:  # 只显示前20个
                print(f"... and {len(overlap_files) - 20} more")
                break
            print(file)
    else:
        print("✅ No overlapping filenames found!")

    return len(overlap_files) > 0, overlap_files


def main():
    """主函数"""
    # 你的具体路径
    train_dir = r"F:\Trackdata\images\train"
    test_dir = r"F:\Trackdata\images\val"

    print("Starting dataset overlap analysis...")
    print(f"Train directory: {train_dir}")
    print(f"Val directory: {test_dir}")
    print("-" * 50)

    # 检查目录是否存在
    if not os.path.exists(train_dir):
        print(f"❌ Error: Train directory does not exist: {train_dir}")
        return

    if not os.path.exists(test_dir):
        print(f"❌ Error: Val directory does not exist: {test_dir}")
        return

    # 1. 先进行文件名检查（快速）
    print("\n🚀 Step 1: Quick filename check...")
    filename_overlap, filename_matches = check_filename_overlap(train_dir, test_dir)

    # 2. 再进行图像哈希检查（较慢但准确）
    print("\n🚀 Step 2: Detailed image hash check...")
    hash_overlap, hash_matches = check_dataset_overlap(train_dir, test_dir)

    # 总结报告
    print("\n" + "=" * 50)
    print("📊 FINAL VALIDATION SUMMARY")
    print("=" * 50)

    if not filename_overlap and not hash_overlap:
        print("✅ SUCCESS: No dataset overlap detected!")
        print("Your training and validation sets are properly separated.")
    else:
        print("❌ WARNING: Dataset overlap detected!")
        print(f"Filename overlaps: {len(filename_matches) if filename_overlap else 0}")
        print(f"Image hash overlaps: {len(hash_matches) if hash_overlap else 0}")
        print("\nRecommendations:")
        print("1. Remove overlapping images from validation set")
        print("2. Re-run model evaluation with clean dataset")
        print("3. Check your dataset splitting procedure")


if __name__ == "__main__":
    main()