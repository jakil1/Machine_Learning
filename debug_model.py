from ultralytics import YOLO

# 1. 加载你的模型
model = YOLO(r'D:/PyCharm/Machine_learning/runs/detect/train2/weights/best.pt')

# 2. 随便找一张图片的路径 (请修改为你文件夹里实际存在的一张图的名字)
# 比如: F:\train_shuffled_final\000001.jpg
img_path = r'F:\train_shuffled_final\cattle000001.jpg' 

print(f"正在让模型看这张图: {img_path} ...")

# 3. 预测，并把门槛降到极低 (0.01)
results = model.predict(img_path, conf=0.01)

# 4. 打印结果
result = results[0]
print("-" * 30)
print(f"模型在这张图里发现了 {len(result.boxes)} 个目标。")

if len(result.boxes) > 0:
    print("目标详情 (类别 | 置信度):")
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        print(f"类别: {cls_id} | 置信度: {conf:.4f}")
else:
    print("😱 完了，模型什么都没看见！(检测数量为 0)")
    print("这说明训练可能出问题了，模型没学到东西。")