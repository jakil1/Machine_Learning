import json
import pandas as pd
import os

# --- 配置部分 ---
log_file = 'log.txt'  # 你的日志文件名，如果路径不同请修改
output_file = 'train_results.xlsx'  # 输出的Excel文件名


# ----------------

def parse_log(file_path):
    data_list = []

    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        print("正在读取日志...")
        for line in f:
            line = line.strip()
            if not line: continue

            try:
                # 日志每行都是一个 JSON 对象
                entry = json.loads(line)

                # 提取我们需要的数据
                row = {
                    'Epoch': entry.get('epoch'),
                    'Train Loss': entry.get('train_loss'),
                    'Learning Rate': entry.get('train_lr'),
                    # 提取具体的 Loss 组件 (可选，方便分析哪里没降)
                    'Loss VFL': entry.get('train_loss_vfl'),
                    'Loss Bbox': entry.get('train_loss_bbox'),
                    'Loss GIoU': entry.get('train_loss_giou'),
                }

                # 提取 mAP 指标 (test_coco_eval_bbox 是一个列表)
                # COCO 标准定义:
                # index 0 = mAP 50-95 (最重要)
                # index 1 = mAP 50 (PASCAL VOC标准)
                # index 2 = mAP 75 (严格标准)
                if 'test_coco_eval_bbox' in entry:
                    metrics = entry['test_coco_eval_bbox']
                    if len(metrics) >= 2:
                        row['mAP_50_95'] = metrics[0]
                        row['mAP_50'] = metrics[1]
                        row['mAP_75'] = metrics[2]

                data_list.append(row)

            except json.JSONDecodeError:
                print(f"跳过无法解析的行: {line[:50]}...")
                continue

    return pd.DataFrame(data_list)


# 执行转换
df = parse_log(log_file)

if df is not None and not df.empty:
    # 按照 Epoch 排序，防止乱序
    df = df.sort_values(by='Epoch')

    # 保存为 Excel
    df.to_excel(output_file, index=False)
    print(f"\n✅ 成功！数据已保存为: {output_file}")
    print(f"共提取了 {len(df)} 个 Epoch 的数据。")
    print("\n前5行预览：")
    print(df[['Epoch', 'Train Loss', 'mAP_50_95', 'mAP_50']].head())
else:
    print("❌ 提取失败，请检查 log.txt 是否为空或格式不正确。")