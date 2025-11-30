import json
import wandb
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体支持（如果不需要中文可以删除这部分）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


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


def upload_complete_training_curves(log_file1, log_file2, label1="Model 1", label2="Model 2"):
    """上传完整的训练曲线到wandb"""

    # 初始化wandb项目
    wandb.init(project="model-comparison-detailed", name="complete_training_curves")

    # 解析log文件
    data1 = parse_log_file(log_file1)
    data2 = parse_log_file(log_file2)

    if data1 is None and data2 is None:
        print("Error: Both log files not found!")
        return

    # 记录每个epoch的数据
    max_epochs = max(len(data1["train_losses"]) if data1 else 0,
                     len(data2["train_losses"]) if data2 else 0)

    for epoch in range(max_epochs):
        log_data = {"epoch": epoch}

        # 记录模型1的数据（如果存在）
        if data1 and epoch < len(data1["train_losses"]):
            log_data[f"{label1}/train_loss"] = data1["train_losses"][epoch]
        if data1 and epoch < len(data1["mAP50s"]):
            log_data[f"{label1}/mAP50"] = data1["mAP50s"][epoch]
        if data1 and epoch < len(data1["train_lrs"]) and data1["train_lrs"]:
            log_data[f"{label1}/learning_rate"] = data1["train_lrs"][epoch]

        # 记录模型2的数据（如果存在）
        if data2 and epoch < len(data2["train_losses"]):
            log_data[f"{label2}/train_loss"] = data2["train_losses"][epoch]
        if data2 and epoch < len(data2["mAP50s"]):
            log_data[f"{label2}/mAP50"] = data2["mAP50s"][epoch]
        if data2 and epoch < len(data2["train_lrs"]) and data2["train_lrs"]:
            log_data[f"{label2}/learning_rate"] = data2["train_lrs"][epoch]

        wandb.log(log_data)

    # 记录最终统计信息
    if data1 and data2:
        summary = {
            f"{label1}_final_loss": data1["train_losses"][-1],
            f"{label1}_final_mAP50": data1["mAP50s"][-1],
            f"{label2}_final_loss": data2["train_losses"][-1],
            f"{label2}_final_mAP50": data2["mAP50s"][-1],
            "loss_difference": data1["train_losses"][-1] - data2["train_losses"][-1],
            "mAP50_difference": data1["mAP50s"][-1] - data2["mAP50s"][-1]
        }
        wandb.log(summary)

    # 完成wandb记录
    wandb.finish()

    print("Complete training curves uploaded to wandb!")

    # 返回解析的数据用于本地绘图
    return data1, data2


def create_local_comparison_plot(data1, data2, label1="Model 1", label2="Model 2"):
    """创建本地对比图"""
    if not data1 and not data2:
        print("No data to plot!")
        return

    plt.figure(figsize=(15, 5))

    # 1. 训练损失对比
    plt.subplot(1, 3, 1)
    if data1:
        epochs1 = data1["epochs"][:len(data1["train_losses"])]
        plt.plot(epochs1, data1["train_losses"], 'b-', label=label1, linewidth=2)
    if data2:
        epochs2 = data2["epochs"][:len(data2["train_losses"])]
        plt.plot(epochs2, data2["train_losses"], 'r-', label=label2, linewidth=2)

    plt.title("Training Loss Comparison")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 2. mAP50对比
    plt.subplot(1, 3, 2)
    if data1:
        epochs1_map = data1["epochs"][:len(data1["mAP50s"])]
        plt.plot(epochs1_map, data1["mAP50s"], 'b-', label=label1, linewidth=2)
    if data2:
        epochs2_map = data2["epochs"][:len(data2["mAP50s"])]
        plt.plot(epochs2_map, data2["mAP50s"], 'r-', label=label2, linewidth=2)

    plt.title("mAP50 Comparison")
    plt.xlabel("Epoch")
    plt.ylabel("mAP50")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 3. 学习率对比（如果有数据）
    if data1 and data1["train_lrs"] and data2 and data2["train_lrs"]:
        plt.subplot(1, 3, 3)
        if data1:
            epochs1_lr = data1["epochs"][:len(data1["train_lrs"])]
            plt.plot(epochs1_lr, data1["train_lrs"], 'b-', label=label1, linewidth=2)
        if data2:
            epochs2_lr = data2["epochs"][:len(data2["train_lrs"])]
            plt.plot(epochs2_lr, data2["train_lrs"], 'r-', label=label2, linewidth=2)

        plt.title("Learning Rate Comparison")
        plt.xlabel("Epoch")
        plt.ylabel("Learning Rate")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')  # 学习率通常用对数坐标

    plt.tight_layout()
    plt.savefig("local_comparison_plot.png", dpi=300, bbox_inches='tight')
    print("Local comparison plot saved: local_comparison_plot.png")


def main():
    """主函数"""
    # 配置两个log文件路径和标签
    log_file1 = "D:/PyCharm/Machine_learning/LeNet/log.txt"
    log_file2 = "D:/PyCharm/Machine_learning/LeNet/log(1).txt"
    label1 = "Model 1"
    label2 = "Model 2"

    print("Starting log comparison...")

    # 上传完整训练曲线到wandb
    data1, data2 = upload_complete_training_curves(log_file1, log_file2, label1, label2)

    # 创建本地对比图
    create_local_comparison_plot(data1, data2, label1, label2)

    # 打印最终统计信息
    if data1 and data2:
        print("\n=== Final Statistics ===")
        print(f"{label1}: Final Loss = {data1['train_losses'][-1]:.4f}, Final mAP50 = {data1['mAP50s'][-1]:.4f}")
        print(f"{label2}: Final Loss = {data2['train_losses'][-1]:.4f}, Final mAP50 = {data2['mAP50s'][-1]:.4f}")
        print(f"Loss Difference: {data1['train_losses'][-1] - data2['train_losses'][-1]:.4f}")
        print(f"mAP50 Difference: {data1['mAP50s'][-1] - data2['mAP50s'][-1]:.4f}")


if __name__ == "__main__":
    main()