import os
import shutil
from PIL import Image
import imagehash
import cv2
import numpy as np


def calculate_exact_hash(image_path):
    """计算精确的图像哈希（抗干扰性较弱，但更准确）"""
    try:
        image = Image.open(image_path)
        # 使用抗干扰性较弱的哈希算法
        hash_value = imagehash.average_hash(image)
        return str(hash_value)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def calculate_structural_similarity(img1_path, img2_path):
    """计算两张图片的结构相似性指数"""
    try:
        # 读取图片
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)

        if img1 is None or img2 is None:
            return 0

        # 调整到相同尺寸
        img1 = cv2.resize(img1, (256, 256))
        img2 = cv2.resize(img2, (256, 256))

        # 转换为灰度图
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # 计算SSIM
        from skimage.metrics import structural_similarity as ssim
        score, _ = ssim(img1_gray, img2_gray, full=True)
        return score
    except Exception as e:
        print(f"Error calculating SSIM: {e}")
        return 0


def find_true_duplicates(train_dir, val_dir, similarity_threshold=0.95):
    """找到真正的重复图片（使用多种方法验证）"""

    print("Step 1: Calculating image hashes...")
    train_hashes = {}
    val_hashes = {}

    # 计算训练集哈希
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                img_hash = calculate_exact_hash(path)
                if img_hash is not None:
                    train_hashes[img_hash] = path

    # 计算验证集哈希
    for root, dirs, files in os.walk(val_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root, file)
                img_hash = calculate_exact_hash(path)
                if img_hash is not None:
                    val_hashes[img_hash] = path

    # 找到哈希相同的图片
    exact_matches = []
    for hash_val in train_hashes:
        if hash_val in val_hashes:
            exact_matches.append((train_hashes[hash_val], val_hashes[hash_val]))

    print(f"Found {len(exact_matches)} exact hash matches")

    # 验证这些匹配是否真的是相同图片
    true_duplicates = []
    questionable_matches = []

    print("Step 2: Verifying matches with structural similarity...")
    for i, (train_path, val_path) in enumerate(exact_matches):
        similarity = calculate_structural_similarity(train_path, val_path)

        if similarity >= similarity_threshold:
            true_duplicates.append(val_path)
            print(f"✅ True duplicate: {similarity:.3f} - {os.path.basename(val_path)}")
        else:
            questionable_matches.append((train_path, val_path, similarity))
            print(f"❓ Questionable: {similarity:.3f} - {os.path.basename(val_path)}")

    return true_duplicates, questionable_matches


def create_verified_clean_set(train_dir, val_dir, output_dir, similarity_threshold=0.95):
    """创建经过验证的干净验证集"""

    print("Starting verified validation set cleanup...")

    # 找到真正的重复
    true_duplicates, questionable = find_true_duplicates(train_dir, val_dir, similarity_threshold)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 复制非重复的图像
    copied_count = 0
    removed_count = 0

    print("Step 3: Creating clean validation set...")
    for root, dirs, files in os.walk(val_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                source_path = os.path.join(root, file)

                # 如果这个图像不在真正的重复列表中，就复制它
                if source_path not in true_duplicates:
                    dest_path = os.path.join(output_dir, file)
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                else:
                    removed_count += 1

    # 保存报告
    report_path = os.path.join(output_dir, "cleaning_report.txt")
    with open(report_path, "w") as f:
        f.write("VALIDATION SET CLEANING REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Similarity threshold: {similarity_threshold}\n")
        f.write(f"Total images in original val set: {copied_count + removed_count}\n")
        f.write(f"Removed true duplicates: {removed_count}\n")
        f.write(f"Remaining images in clean set: {copied_count}\n")
        f.write(f"Questionable matches (needs manual review): {len(questionable)}\n\n")

        f.write("TRUE DUPLICATES REMOVED:\n")
        f.write("-" * 30 + "\n")
        for dup in true_duplicates:
            f.write(f"{dup}\n")

        f.write("\nQUESTIONABLE MATCHES (needs review):\n")
        f.write("-" * 40 + "\n")
        for train_path, val_path, similarity in questionable:
            f.write(f"Similarity: {similarity:.3f}\n")
            f.write(f"Train: {train_path}\n")
            f.write(f"Val:   {val_path}\n")
            f.write("-" * 20 + "\n")

    print(f"\n✅ Verified clean validation set created in: {output_dir}")
    print(f"📊 Report: {removed_count} duplicates removed, {copied_count} images kept")
    print(f"❓ {len(questionable)} questionable matches need manual review")
    print(f"📄 Detailed report: {report_path}")

    return copied_count, removed_count, questionable


def manual_review_questionable(questionable_matches, review_threshold=0.8):
    """手动审查可疑匹配"""
    print("\n" + "=" * 50)
    print("MANUAL REVIEW RECOMMENDATION")
    print("=" * 50)

    high_similarity = [(t, v, s) for t, v, s in questionable_matches if s >= review_threshold]
    low_similarity = [(t, v, s) for t, v, s in questionable_matches if s < review_threshold]

    print(f"High similarity matches (>= {review_threshold}): {len(high_similarity)}")
    print(f"Low similarity matches (< {review_threshold}): {len(low_similarity)}")

    if high_similarity:
        print("\nConsider reviewing these high-similarity matches:")
        for train_path, val_path, similarity in high_similarity[:5]:  # 只显示前5个
            print(f"  Similarity: {similarity:.3f}")
            print(f"  Train: {os.path.basename(train_path)}")
            print(f"  Val:   {os.path.basename(val_path)}")

    return high_similarity, low_similarity


# 主执行函数
def main():
    train_dir = r"F:\Trackdata\images\train"
    val_dir = r"F:\Trackdata\images\val"
    clean_val_dir = r"F:\Trackdata\images\val_clean_verified"

    # 设置相似度阈值（0.95 = 95%相似度）
    similarity_threshold = 0.95

    print("Starting VERIFIED validation set cleanup...")
    print(f"Using similarity threshold: {similarity_threshold}")

    copied, removed, questionable = create_verified_clean_set(
        train_dir, val_dir, clean_val_dir, similarity_threshold
    )

    # 提供手动审查建议
    high_sim, low_sim = manual_review_questionable(questionable)

    print(f"\n🎯 FINAL RESULT:")
    print(f"Clean validation set: {clean_val_dir}")
    print(f"Total images: {copied}")
    print(f"Removed duplicates: {removed}")
    print(f"High-similarity matches to review: {len(high_sim)}")


if __name__ == "__main__":
    main()