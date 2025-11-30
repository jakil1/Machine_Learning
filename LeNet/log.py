import json
import wandb


def parse_log_file(log_path):
    """解析单个log文件，提取训练数据"""
    epochs = []
    train_losses = []
    mAP50s = []
    train_lrs = []

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                except:
                    continue

                # 提取epoch
                if "epoch" in data:
                    epochs.append(data["epoch"])

                # 提取训练loss
                if "train_loss" in data:
                    train_losses.append(data["train_loss"])

                # 提取mAP50
                if "test_coco_eval_bbox" in data:
                    ap_list = data["test_coco_eval_bbox"]
                    if len(ap_list) > 1:
                        mAP50s.append(ap_list[1])

                # 提取学习率（如果有）
                if "train_lr" in data:
                    train_lrs.append(data["train_lr"])

    except FileNotFoundError:
        print(f"Warning: File not found {log_path}")
        return None

    return {
        "epochs": epochs,
        "train_losses": train_losses,
        "mAP50s": mAP50s,
        "train_lrs": train_lrs
    }


# 配置两个log文件路径
log_file1 = "D:/PyCharm/Machine_learning/LeNet/log.txt"
log_file2 = "D:/PyCharm/Machine_learning/LeNet/log(1).txt"

# 解析log文件
data1 = parse_log_file(log_file1)
data2 = parse_log_file(log_file2)

if data1 is None and data2 is None:
    print("Error: Both log files not found!")
    exit()

# 初始化wandb项目
wandb.init(project="model-comparison", name="log_comparison")

# 方法1: 创建自定义图表
if data1 and data2:
    # 创建损失对比图表
    loss_data = []
    for i, epoch in enumerate(data1["epochs"][:len(data1["train_losses"])]):
        loss_data.append([epoch, data1["train_losses"][i], "Model 1"])
    for i, epoch in enumerate(data2["epochs"][:len(data2["train_losses"])]):
        loss_data.append([epoch, data2["train_losses"][i], "Model 2"])

    # 创建mAP50对比图表
    map_data = []
    for i, epoch in enumerate(data1["epochs"][:len(data1["mAP50s"])]):
        map_data.append([epoch, data1["mAP50s"][i], "Model 1"])
    for i, epoch in enumerate(data2["epochs"][:len(data2["mAP50s"])]):
        map_data.append([epoch, data2["mAP50s"][i], "Model 2"])

    # 记录自定义图表
    wandb.log({
        "loss_comparison": wandb.plot.line_series(
            xs=[row[0] for row in loss_data if row[2] == "Model 1"],
            ys=[[row[1] for row in loss_data if row[2] == "Model 1"],
                [row[1] for row in loss_data if row[2] == "Model 2"]],
            keys=["Model 1", "Model 2"],
            title="Training Loss Comparison",
            xname="Epoch"
        ),
        "mAP50_comparison": wandb.plot.line_series(
            xs=[row[0] for row in map_data if row[2] == "Model 1"],
            ys=[[row[1] for row in map_data if row[2] == "Model 1"],
                [row[1] for row in map_data if row[2] == "Model 2"]],
            keys=["Model 1", "Model 2"],
            title="mAP50 Comparison",
            xname="Epoch"
        )
    })

# 方法2: 直接记录最终结果进行对比
if data1 and data2:
    summary = {
        "Model1_final_loss": data1["train_losses"][-1],
        "Model1_final_mAP50": data1["mAP50s"][-1],
        "Model2_final_loss": data2["train_losses"][-1],
        "Model2_final_mAP50": data2["mAP50s"][-1],
        "loss_difference": data1["train_losses"][-1] - data2["train_losses"][-1],
        "mAP50_difference": data1["mAP50s"][-1] - data2["mAP50s"][-1]
    }
    wandb.log(summary)

# 完成wandb记录
wandb.finish()

print("Results uploaded to wandb!")