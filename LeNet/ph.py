import os
import cv2
import numpy as np

# 这里改成你要去重的那个“图片文件夹”
FOLDER_PATH = r"F:\cattle\train"

# 相似度阈值：越大删得越狠（建议 10~15）
HASH_THRESHOLD = 7


def ahash(image, hash_size=8):
    """平均哈希 aHash"""
    img = cv2.resize(image, (hash_size, hash_size), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    avg = gray.mean()
    hash_bits = (gray >= avg).astype(np.uint8).flatten()
    return hash_bits


def hamming_distance(h1, h2):
    return np.count_nonzero(h1 != h2)


def dedup_folder(folder_path):
    exts = (".jpg", ".jpeg", ".png", ".bmp")
    files = [f for f in os.listdir(folder_path)
             if f.lower().endswith(exts)]

    if not files:
        print(f"[跳过] {folder_path} 没有图片文件")
        return

    files.sort()
    print(f"[处理文件夹] {folder_path}，共 {len(files)} 张图片")

    last_hash = None
    kept = 0
    removed = 0

    for fname in files:
        fpath = os.path.join(folder_path, fname)
        img = cv2.imread(fpath)
        if img is None:
            print(f"  [跳过] 无法读取: {fname}")
            continue

        cur_hash = ahash(img)

        if last_hash is None:
            last_hash = cur_hash
            kept += 1
            print(f"  [保留] {fname} (第一张)")
            continue

        dist = hamming_distance(cur_hash, last_hash)

        if dist <= HASH_THRESHOLD:
            # 太相似，删掉当前图
            try:
                os.remove(fpath)
                removed += 1
                print(f"  [删除] {fname} (与上一张距离 {dist})")
            except Exception as e:
                print(f"  [错误] 删除失败 {fname}: {e}")
        else:
            last_hash = cur_hash
            kept += 1
            print(f"  [保留] {fname} (与上一张距离 {dist})")

    print(f"[完成] {folder_path}：保留 {kept} 张，删除 {removed} 张")


if __name__ == "__main__":
    if not os.path.isdir(FOLDER_PATH):
        print("文件夹不存在：", FOLDER_PATH)
    else:
        dedup_folder(FOLDER_PATH)