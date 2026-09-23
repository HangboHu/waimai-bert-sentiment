from pathlib import Path

import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer

from common.preprocess import clean_text_for_bert


def load_corpus(corpus_file: str | Path) -> list[tuple[str, int]]:
    with open(corpus_file, encoding='utf-8') as file_obj:
        content = file_obj.read()

    corpus = []
    for line in content.splitlines():
        line = clean_text_for_bert(line)
        label, text = line.split(',', maxsplit=1)
        corpus.append((text, int(label)))

    return corpus


class WaimaiDataset(Dataset):
    """投满分数据集"""
    def __init__(self, corpus: list[tuple[str, int]], tokenizer: BertTokenizer, max_len: int=32):
        super().__init__()
        self.corpus = corpus
        self.tokenizer = tokenizer
        self.max_len = max_len


    def __len__(self) -> int:
        return len(self.corpus)


    def __getitem__(self, idx: int) -> dict:
        text, label = self.corpus[idx]
        inputs = self.tokenizer(
            text=text,
            return_tensors='pt',
            padding='max_length',
            truncation=True,
            max_length=self.max_len,
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'label': torch.tensor(label,dtype=torch.int64)
        }