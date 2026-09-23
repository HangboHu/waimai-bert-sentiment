"""模型训练"""
import random
import time

import torch
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from training.config  import Config
from training.dataset import load_corpus, WaimaiDataset


def train():
    """训练模型"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    corpus = load_corpus(Config.train_raw_file)
    # samples = random.sample(corpus, k=24000)
    tokenizer = AutoTokenizer.from_pretrained(Config.bert_model_dir)
    dataset = WaimaiDataset(corpus, tokenizer)
    dataloader = DataLoader(
        dataset=dataset,
        batch_size=256,             # 批大小
        shuffle=True,               # 随机乱序
        drop_last=True,             # 是否允许丢到不成批的最后一组数据
        num_workers=4,              # 进程数
        persistent_workers=True,    # 保留进程
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        Config.bert_model_dir,
        num_labels=2,
    )

    for parameter in model.bert.embeddings.parameters():
        parameter.requires_grad = False

    for layer in model.bert.encoder.layer[:3]:
        for parameter in layer.parameters():
            parameter.requires_grad = False

    model.to(device)

    loss_func = CrossEntropyLoss()
    optimizer = AdamW([
        {'params': model.bert.encoder.layer[6:].parameters(), 'lr': 1e-5},
        {'params': model.classifier.parameters(), 'lr': 2e-4},
    ])

    for epoch in range(20):
        start = time.perf_counter()
        model.train()

        total_loss = 0.0
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            label = batch['label'].to(device)
            # 梯度清零
            optimizer.zero_grad()
            # 正向传播
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
            # 计算损失
            loss = loss_func(outputs.logits, label)
            # 反向传播
            loss.backward()
            # 参数更新
            optimizer.step()
            total_loss += loss.item()
        end = time.perf_counter()
        print(f'Epoch:{epoch+1}, Loss:{total_loss/len(dataloader):.3f}, time:{end-start:.3f}s')

    # 保存模型
    tokenizer.save_pretrained(Config.model_file)
    model.save_pretrained(Config.model_file)