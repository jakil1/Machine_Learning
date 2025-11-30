from ultralytics import YOLO

if __name__ == '__main__':
    # 1. 加载模型
    model = YOLO('yolov8n.pt') 

    # 2. 开始训练
    # 指向刚才写好的 data.yaml
    model.train(data=r'F:\cattle2\data.yaml', epochs=50, imgsz=640, batch=4, workers=0)