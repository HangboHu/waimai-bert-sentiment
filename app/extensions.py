"""
extensions - 扩展功能
"""
from threading import Lock
import torch

from flask import Flask
from transformers import AutoModelForSequenceClassification, AutoTokenizer



class TextClassifierExtension:
    """文本分类器单例扩展"""

    def __init__(self, app: Flask=None):
        self._class_file = None
        self._model_path = None
        self._class_labels = None
        self._preprocessor = None
        self._tokenizer = None
        self._model = None
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu'
        )
        self._lock = Lock()

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """挂载到 Flask 实例"""
        self._class_file = app.config['CLASS_FILE']
        self._model_path = app.config['MODEL_PATH']
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['text_classifier'] = self

    def warmup(self):
        """模型预热方法"""
        _ = self.model, self.class_labels, self.tokenizer
        # self.model.predict("hello world")   # 将重要参数加载到缓存


    @property
    def model(self):
        """延迟加载模型"""
        if self._model is None:
            with self._lock:
                if self._model is None:
                    print("=======正在加载模型========")
                    self._model = AutoModelForSequenceClassification.from_pretrained(self._model_path).to(self.device)
                    self._model.eval()
                    print("=======模型加载完成========")
        return self._model


    @property
    def class_labels(self):
        """延迟加载类别标签"""
        if self._class_labels is None:
            with self._lock:
                if self._class_labels is None:
                    with open(self._class_file, encoding='utf-8') as file_obj:
                        self._class_labels = [line.strip() for line in file_obj if line.strip()]
        return self._class_labels


    @property
    def tokenizer(self):
        """延迟加载分词器"""
        if self._tokenizer is None:
            with self._lock:
                if self._tokenizer is None:
                    self._tokenizer = AutoTokenizer.from_pretrained(self._model_path)
        return self._tokenizer


# 创建扩展对象
thy_extension = TextClassifierExtension()
