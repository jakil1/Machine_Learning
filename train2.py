from ultralytics import YOLO


def main():
    # 1. 这里填你训练好的 best.pt 的绝对路径
    # 例如: D:\PyCharm\Machine_learning\runs\detect\train\weights\best.pt
    model_path = r"F:/cattle_train/runs/cow_detect_exp1/weights/best.pt"

    # 2. 加载模型
    model = YOLO(model_path)

    # 3. 运行验证 (画图)
    # 关键修改：
    # split='test' -> 用测试集跑 (如果你有单独的test)
    # workers=0    -> 【核心】强制使用单线程，完美解决 Windows 报错！
    # plots=True   -> 强制画图
    metrics = model.val(
        data='cow_data.yaml',  # 你的数据集配置文件
        split='test',  # 或者 'val'，看你想测哪个集
        workers=0,  # 必填！设为0就不会报错了
        plots=True  # 必填！告诉它要把图画出来
    )

    print("✅ 图表生成完毕！请去 runs/detect/val... 文件夹查看")


if __name__ == '__main__':
    main()
