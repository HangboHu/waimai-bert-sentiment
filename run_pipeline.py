import sys
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))


def main():
    """离线训练流水线程序入口"""
    print("\n=== [Step 1/5] 开始执行数据清洗和准备工作 ===")
    # Todo: 执行数据清洗和准备

    print("\n=== [Step 2/5] 开始训练和导出文本分类模型 ===")
    # Todo: 执行模型训练和导出

    print("\n=== [Step 3/5] 启动服务之前对模型进行评估 ===")
    # Todo: 执行模型推理和评估

    print("\n=== [Step 4/5] 启动服务之前对模型进行压缩 ===")
    # Todo: 执行模型压缩

    print("\n=== [Step 5/5] 启动服务之前对压缩模型进行评估 ===")
    # Todo: 执行压缩后的模型评估

if __name__ == "__main__":
    main()
