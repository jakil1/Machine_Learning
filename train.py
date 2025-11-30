from ultralytics import YOLO

if __name__ == '__main__':
    # 1. 加载模型
    model = YOLO('yolo11n.pt')

    # 2. 开始训练
    results = model.train(
        data='cow_data.yaml',
        epochs=150,
        imgsz=640,
        batch=16,
        device=0,
        workers=0,  # Windows下建议设为0，防止报错

        # ⚠️ 关键修改：指定保存路径
        # project: 总文件夹路径 (建议设在 F:/cattle_train/runs)
        project=r'F:\cattle_train\runs',

        # name: 这次训练的具体子文件夹名
        name='cow_detect_exp1'
    )

    print(f"训练完成！结果已保存在: F:\\cattle_train\\runs\\cow_detect_exp1")