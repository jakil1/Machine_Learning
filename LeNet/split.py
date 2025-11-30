import os
import json
import cv2
from collections import defaultdict
import argparse


def convert_yolo_to_coco(data_dir, output_dir, classes):
    """
    将YOLO格式数据集转换为COCO格式
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 类别映射
    categories = []
    for i, class_name in enumerate(classes):
        categories.append({
            "id": i + 1,  # COCO格式类别ID从1开始
            "name": class_name,
            "supercategory": "animal"
        })

    # 处理训练集和验证集
    for split in ['train', 'val']:
        images_dir = os.path.join(data_dir, 'images', split)
        labels_dir = os.path.join(data_dir, 'labels', split)

        if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
            print(f"跳过 {split} 集，目录不存在")
            continue

        # 获取所有图像文件
        image_files = [f for f in os.listdir(images_dir)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        coco_output = {
            "images": [],
            "annotations": [],
            "categories": categories
        }

        image_id = 1
        annotation_id = 1

        for image_file in image_files:
            # 读取图像获取尺寸
            image_path = os.path.join(images_dir, image_file)
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图像: {image_path}")
                continue

            height, width = img.shape[:2]

            # 添加图像信息
            coco_output["images"].append({
                "id": image_id,
                "file_name": image_file,
                "width": width,
                "height": height
            })

            # 读取对应的标签文件
            label_file = os.path.splitext(image_file)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_file)

            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 解析YOLO格式: class_id x_center y_center width height
                    parts = line.split()
                    if len(parts) != 5:
                        continue

                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    w = float(parts[3])
                    h = float(parts[4])

                    # 转换为COCO格式: [x_min, y_min, width, height] 绝对坐标
                    x_min = (x_center - w / 2) * width
                    y_min = (y_center - h / 2) * height
                    bbox_width = w * width
                    bbox_height = h * height

                    # 计算面积
                    area = bbox_width * bbox_height

                    # 添加标注信息
                    coco_output["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": class_id + 1,  # YOLO从0开始，COCO从1开始
                        "bbox": [x_min, y_min, bbox_width, bbox_height],
                        "area": area,
                        "iscrowd": 0
                    })

                    annotation_id += 1

            image_id += 1

        # 保存COCO格式的JSON文件
        output_file = os.path.join(output_dir, f'instances_{split}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_output, f, ensure_ascii=False, indent=2)

        print(f"{split}集转换完成:")
        print(f"  图像数量: {len(coco_output['images'])}")
        print(f"  标注数量: {len(coco_output['annotations'])}")
        print(f"  输出文件: {output_file}")


if __name__ == "__main__":
    # 配置参数
    data_dir = r"F:\Trackdata"
    output_dir = os.path.join(data_dir, "annotations")
    classes = ['calf', 'cattle']  # 确保与YOLO标签中的类别顺序一致

    convert_yolo_to_coco(data_dir, output_dir, classes)