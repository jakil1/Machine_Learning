import os
import shutil

def merge_dataset_images():
    # --- 这里是你可以直接修改的配置 ---
    
    # 1. 你的大文件夹路径 (程序会自动扫描这个文件夹下的所有子文件夹)
    # 注意：路径字符串前面加 r 可以防止转义字符报错
    source_dir = r"F:\dataset"  
    
    # 2. 合并后的图片存放位置 (如果不存在会自动创建)
    target_dir = r"F:\cattle3\train_merged_all"
    
    # --------------------------------
    
    # 支持的图片格式
    img_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    count = 0
    print(f"正在扫描大文件夹: {source_dir} ...")

    # os.walk 会自动一层层往下找，你不需要输入 D01 那一层的路径
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in img_extensions:
                # 获取当前子文件夹的名字，例如 "D01_20231101235950"
                folder_name = os.path.basename(root)
                
                # 跳过大文件夹根目录本身，防止重复处理
                if root == source_dir:
                    continue

                # --- 核心重命名逻辑 ---
                # 新名字 = 文件夹名 + "_" + 原文件名
                # 结果示例: D01_20231101235950_0001.jpg
                new_filename = f"{folder_name}_{file}"
                
                # 构建完整路径
                src_path = os.path.join(root, file)
                dst_path = os.path.join(target_dir, new_filename)

                # 防止极少数情况下的重名 (自动加数字后缀)
                duplicate_count = 1
                while os.path.exists(dst_path):
                    name_no_ext = os.path.splitext(new_filename)[0]
                    dst_path = os.path.join(target_dir, f"{name_no_ext}_{duplicate_count}{ext}")
                    duplicate_count += 1

                try:
                    shutil.copy2(src_path, dst_path)
                    count += 1
                    # 打印进度 (可选，嫌刷屏可以注释掉)
                    print(f"处理: {folder_name} -> {new_filename}")
                except Exception as e:
                    print(f"错误: {src_path} -> {e}")

    print("-" * 30)
    print(f"搞定！共合并了 {count} 张图片。")
    print(f"文件保存在: {target_dir}")

if __name__ == '__main__':
    merge_dataset_images()