"""
config - 全局配置项
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    """基础配置类（所有环境共享的公共配置）"""

    # 核心安全密匙（生产环境必须在 .env 中覆盖它）
    # openssl rand -hex 32
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-for-dev')

    # 数据库通用配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 模型持久化文件路径
    MODEL_PATH = os.getenv('MODEL_PATH', str(BASE_DIR / 'model' / 'ft_bert_dir'))
    CLASS_FILE = os.getenv('CLASS_FILE', str(BASE_DIR / 'model' / 'thy_labels.txt'))



class DevelopmentConfig(BaseConfig):
    """开发环境配置"""

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / 'app_dev.db'}'
    )


class ProductionConfig(BaseConfig):
    """生产环境配置"""

    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'max_overflow': 20
    }


class TestingConfig(BaseConfig):
    """测试环境配置"""
    pass


# 不同环境对应的配置类
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
}
