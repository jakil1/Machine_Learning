import os
import hashlib
import shutil


def calculate_md5(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def find_exact_duplicates_by_md5(train_dir, val_dir):
    """使用MD5找到完全相同的文件"""
    train_md5 = {}
    val_md5 = {}

    print("Calculating MD5 for training images...")
    train_count = 0
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                md5_val = calculate_md5(path)
                if md5_val:
                    train_md5[md5_val] = path
                train_count += 1
                if train_count % 100 == 0:
                    print(f"Processed {train_count} training images...")

    print("Calculating MD5 for validation images...")
    val_count = 0
    for root, dirs, files in os.walk(val_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                md5_val = calculate_md5(path)
                if md5_val:
                    val_md5[md5_val] = path
                val_count += 1
                if val_count % 100 == 0:
                    print(f"Processed {val_count} validation images...")

    # 找到MD5相同的文件
    train_md5_set = set(train_md5.keys())
    val_md5_set = set(val_md5.keys())
    exact_duplicates_md5 = train_md5_set.intersection(val_md5_set)

    exact_duplicates = [val_md5[md5] for md5 in exact_duplicates_md5]

    print(f"\n=== MD5 Exact Duplicate Analysis ===")
    print(f"Training images: {len(train_md5)}")
    print(f"Validation images: {len(val_md5)}")
    print(f"Exact duplicates (MD5 match): {len(exact_duplicates)}")

    return exact_duplicates


def create_md5_clean_validation_set(train_dir, val_dir, output_dir):
    """基于MD5创建干净的验证集"""

    print("Starting MD5-based validation set cleanup...")

    # 找到完全相同的文件
    exact_duplicates = find_exact_duplicates_by_md5(train_dir, val_dir)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 复制非重复的图像
    copied_count = 0
    removed_count = 0

    print("Creating clean validation set...")
    for root, dirs, files in os.walk(val_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                source_path = os.path.join(root, file)

                # 如果这个图像不在完全重复列表中，就复制它
                if source_path not in exact_duplicates:
                    dest_path = os.path.join(output_dir, file)
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                else:
                    removed_count += 1

    # 保存报告
    report_path = os.path.join(output_dir, "md5_cleaning_report.txt")
    with open(report_path, "w") as f:
        f.write("MD5-BASED VALIDATION SET CLEANING REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Exact duplicates removed: {removed_count}\n")
        f.write(f"Remaining images in clean set: {copied_count}\n\n")

        f.write("EXACT DUPLICATES REMOVED (MD5 match):\n")
        f.write("-" * 40 + "\n")
        for dup in exact_duplicates:
            f.write(f"{dup}\n")

    print(f"\n✅ MD5-based clean validation set created in: {output_dir}")
    print(f"📊 Removed {removed_count} exact duplicates, kept {copied_count} images")
    print(f"📄 Detailed report: {report_path}")

    return copied_count, removed_count


def manual_check_specific_pairs(pairs_to_check):
    """手动检查特定的图像对"""
    print("\n=== MANUAL CHECK FOR SPECIFIC PAIRS ===")

    for i, (train_path, val_path) in enumerate(pairs_to_check):
        if os.path.exists(train_path) and os.path.exists(val_path):
            # 计算MD5
            train_md5 = calculate_md5(train_path)
            val_md5 = calculate_md5(val_path)

            # 获取文件大小
            train_size = os.path.getsize(train_path)
            val_size = os.path.getsize(val_path)

            print(f"\nPair {i + 1}:")
            print(f"Train: {os.path.basename(train_path)} (Size: {train_size} bytes, MD5: {train_md5})")
            print(f"Val:   {os.path.basename(val_path)} (Size: {val_size} bytes, MD5: {val_md5})")

            if train_md5 == val_md5:
                print("✅ EXACT DUPLICATE (MD5 match)")
            else:
                print("❌ DIFFERENT FILES (MD5 differ)")
        else:
            print(f"❌ File not found: {train_path} or {val_path}")


def main():
    """主函数"""
    train_dir = r"F:\Trackdata\images\train"
    val_dir = r"F:\Trackdata\images\val"
    clean_val_dir = r"F:\Trackdata\images\val_clean_md5"

    print("Starting MD5-based exact duplicate removal...")
    print(f"Train directory: {train_dir}")
    print(f"Val directory: {val_dir}")
    print(f"Clean val directory: {clean_val_dir}")
    print("-" * 50)

    # 检查目录是否存在
    if not os.path.exists(train_dir):
        print(f"❌ Error: Train directory does not exist: {train_dir}")
        return

    if not os.path.exists(val_dir):
        print(f"❌ Error: Val directory does not exist: {val_dir}")
        return

    # 创建基于MD5的干净验证集
    copied, removed = create_md5_clean_validation_set(train_dir, val_dir, clean_val_dir)

    print("\n" + "=" * 50)
    print("🎯 MD5 CLEANUP COMPLETED")
    print("=" * 50)
    print(f"✅ Created clean validation set with {copied} images")
    print(f"❌ Removed {removed} EXACT duplicates (MD5 match)")
    print(f"📁 Clean validation set: {clean_val_dir}")

    # 手动检查一些特定的对（从你的列表中选取）
    print("\n" + "=" * 50)
    print("MANUAL VERIFICATION OF SPECIFIC PAIRS")
    print("=" * 50)

    pairs_to_check = [
        (r"F:\Trackdata\images\train\9_5_0.jpg", r"F:\Trackdata\images\val\9_5_0.jpg"),
        (r"F:\Trackdata\images\train\6_3_15.jpg", r"F:\Trackdata\images\val\6_3_15.jpg"),
        (r"F:\Trackdata\images\train\cattle150.jpg", r"F:\Trackdata\images\val\cattle151.jpg"),
        (r"F:\Trackdata\images\train\cattle680.jpg", r"F:\Trackdata\images\val\cattle1800.jpg"),
    ]

    manual_check_specific_pairs(pairs_to_check)

    print("\nNext steps:")
    print("1. Use the new clean validation set for model evaluation")
    print("2. Compare the results with previous evaluations")
    print("3. If accuracy is still suspiciously high, consider visual similarity issues")


if __name__ == "__main__":
    main()