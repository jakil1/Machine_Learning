import torch.nn as nn
criterion = nn.KLDivLoss(reduction='batchmean')
# 输入通常需要是 Log-probabilities (即 log_softmax 的结果)
loss = criterion(torch.log_softmax(output, dim=1), target_distribution)