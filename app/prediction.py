"""
prediction - API 接口实现
"""
import torch
from flask import Blueprint, request, current_app

from common.preprocess import clean_text_for_bert

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1_bp.route('/', methods=['GET', 'POST'])
def home():
    """接口根目录"""
    return {'code': 200, 'message': 'API v1'}


@api_v1_bp.route('/labels', methods=['GET', 'POST'])
def labels():
    """获取所有类别标签"""
    thy_extension = current_app.extensions['text_classifier']
    return {'code': 200, 'results': thy_extension.class_labels}


def texts_process_predict(texts):
    """文本处理与模型预测复用函数"""
    if texts is None:
        return {'code': 400, 'message': '缺少 text 字段'}, 400
    if isinstance(texts, str):
        texts = [texts]
    elif not isinstance(texts, list):
        return {
            'code': 400,
            'message': 'text 字段应为字符串或字符串数组',
        }, 400

    if not texts:
        return {'code': 400, 'message': '没有可识别的文本'}, 400

    thy_extension = current_app.extensions['text_classifier']

    # 调用函数处理文本
    x_test = list(map(clean_text_for_bert, texts))
    # 通过扩展对象加载训练好的分词器,模型和类别标签
    tokenizer = thy_extension.tokenizer
    model = thy_extension.model
    class_labels = thy_extension.class_labels

    # 模型推理,阻断计算图
    with torch.inference_mode():
        inputs = tokenizer(
            text=x_test,
            return_tensors='pt',
            max_length=32,
            truncation=True,
            padding='max_length',
        ).to(thy_extension.device)

        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        confids, labels = torch.max(probs, dim=-1)
        labels = labels.cpu().tolist()
        confids = confids.cpu().tolist()

    results = []
    for text, label, confid in zip(texts, labels, confids):
        results.append({
            'text': text,
            'label': class_labels[int(label)],
            'confidence': f'{confid:.2%}',
            'is_certain': bool(confid >= 0.8)
        })
    return {'code': 200, 'results': results}


@api_v1_bp.route('/classify', methods=['POST'])
def classify():
    """调用模型推理"""
    payload = request.get_json(silent=True, force=True) or {}
    texts = payload.get('text')

    result = texts_process_predict(texts)

    return result


@api_v1_bp.route('/classify_from_file', methods=['POST'])
def classify_from_file():
    """调用模型进行文件推理"""
    # 通过请求对象获取上传文件
    file_obj = request.files.get('text_file')
    if not file_obj or not file_obj.filename:
        return {'code': 400, 'message': '没有读取到上传的文件'}, 400
    content = file_obj.read().decode('utf-8')
    texts = [line.strip() for line in content.splitlines() if line.strip()]
    if not texts:
        return {'code': 400, 'message': '文件里没有可识别的文本'}, 400

    result = texts_process_predict(texts)

    return result
