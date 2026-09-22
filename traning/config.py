from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    """配置类"""
    train_raw_file:    Path = BASE_DIR / 'data/raw' / 'train.csv'
    valid_raw_file:    Path = BASE_DIR / 'data/raw' / 'valid.csv'
    test_raw_file:     Path = BASE_DIR / 'data/raw' / 'test.csv'

    train_pre_file:    Path = BASE_DIR / 'data/pre' / 'tmf_train.txt'
    valid_pre_file:    Path = BASE_DIR / 'data/pre' / 'tmf_valid.txt'

    model_file:        Path = BASE_DIR / 'model' / 'ft_bert_dir'
    bert_model_dir:    Path = BASE_DIR / 'model' / 'google-bert/bert-base-chinese'