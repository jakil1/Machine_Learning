from ultralytics import YOLO
import os
from tqdm import tqdm  # 进度条库，如果没有安装: pip install tqdm

# ================= 配置区域 =================
# 1. 刚才训练好的模型路径 (请去 runs/detect/train/weights/ 找 best.pt)
# 注意：如果是 train2, train3，记得改路径
MODEL_PATH = r'D:/PyCharm/Machine_learning/runs/detect/train2/weights/best.pt'

# 2. 剩下的几千张未标注图片的文件夹路径
# 注意：这里填的是纯图片文件夹，不要混杂其他东西
IMAGES_DIR = r'F:/train_shuffled_final'  

# 3. 置信度阈值 (0~1)
# 建议设为 0.2 或 0.25。
# 设太高(0.5)会导致漏标，设太低(0.1)会导致乱标。
CONF_THRESHOLD = 0.25
# ===========================================

def auto_label():
    print(f"正在加载模型: {MODEL_PATH} ...")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"模型加载失败！请检查路径是否正确。\n错误: {e}")
        return

    # 获取所有图片列表
    valid_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = [f for f in os.listdir(IMAGES_DIR) if os.path.splitext(f)[1].lower() in valid_exts]
    
    print(f"找到 {len(image_files)} 张图片，开始自动标注...")
    print("生成的 .txt 文件将直接保存在图片文件夹里。")

    # 开始遍历预测
    for img_file in tqdm(image_files):
        img_path = os.path.join(IMAGES_DIR, img_file)
        
        # 核心预测代码
        # save=False: 我们自己处理保存逻辑，不让它存到 runs 文件夹里去
        results = model.predict(img_path, conf=CONF_THRESHOLD, iou=0.45, verbose=False)
        
        # 处理结果
        for result in results:
            # 构造 txt 文件路径 (与图片同名，同目录)
            txt_filename = os.path.splitext(img_file)[0] + ".txt"
            txt_path = os.path.join(IMAGES_DIR, txt_filename)
            
            # 将预测结果写入 txt
            # result.save_txt() 是 YOLO 自带的存文件功能，方便快捷
            # save_conf=False: LabelImg 不需要置信度，所以填 False
            result.save_txt(txt_path, save_conf=False)

    print("-" * 30)
    print("🎉 自动标注完成！")
    print(f"请打开 LabelImg，加载目录: {IMAGES_DIR}")
    print("现在你应该能看到框已经画好了，请开始人工修正（改作业）。")

if __name__ == '__main__':
    auto_label()