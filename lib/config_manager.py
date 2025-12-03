"""
配置管理模块
处理配置文件加载和验证
"""
import os
import yaml
from pathlib import Path
from .logger_config import setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file=None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认位置
        """
        if config_file is None:
            # 使用相对于项目根目录的默认配置文件
            script_dir = Path(__file__).parent.parent
            config_file = script_dir / "config.yaml"
        
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            logger.error(f"配置文件未找到: {self.config_file}")
            raise FileNotFoundError(f"配置文件未找到: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {self.config_file}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def get_fal_key(self):
        """
        获取FAL API密钥
        优先级：环境变量 > 配置文件
        """
        api_key = os.getenv('FAL_KEY') or self.config.get('fal_key', '')
        
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            logger.error("FAL API密钥未配置。请在config.yaml中设置或通过FAL_KEY环境变量设置")
            raise ValueError("FAL API密钥未配置")
        
        return api_key
    
    def get_models(self, task_type):
        """
        获取指定任务类型的模型配置
        
        Args:
            task_type: 任务类型 (text_to_image, text_to_video, image_to_image, image_to_video)
            
        Returns:
            模型配置字典
        """
        config_key = f"{task_type}_models"
        models = self.config.get(config_key, {})
        
        if not models:
            logger.warning(f"未找到 {config_key} 配置")
        
        return models
    
    def validate_models(self, models):
        """
        验证模型配置
        
        Args:
            models: 模型配置字典
            
        Returns:
            是否有效
        """
        if not models:
            logger.error("模型配置为空")
            return False
        
        for model_name, model_info in models.items():
            if not isinstance(model_info, dict):
                logger.error(f"模型 {model_name} 配置格式错误")
                return False
            
            if 'model_path' not in model_info:
                logger.error(f"模型 {model_name} 缺少 model_path 配置")
                return False
        
        return True
