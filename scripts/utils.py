"""
通用工具模块
提供配置加载、日志设置、结果提取等通用功能
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional


def setup_logging(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """设置日志配置"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(name)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: 配置文件格式错误
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"配置文件格式错误: {e}")


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    验证 API 密钥是否有效
    
    Args:
        api_key: API 密钥
        
    Returns:
        是否有效
    """
    if not api_key or api_key.strip() == "":
        return False
    if api_key == "YOUR_API_KEY_HERE":
        return False
    # 检查是否是占位符格式
    if "YOUR" in api_key.upper() or "REPLACE" in api_key.upper():
        return False
    return True


def extract_result_url(result: Any, result_type: str = "image") -> str:
    """
    从 API 返回结果中提取 URL
    
    Args:
        result: API 返回的结果对象
        result_type: 结果类型，可选 "image" 或 "video"
        
    Returns:
        提取的 URL 字符串，失败时返回错误信息
    """
    try:
        # 处理字典类型结果
        if isinstance(result, dict):
            # 直接包含 url 字段
            if "url" in result:
                return result["url"]
            
            # 包含 images 列表
            if result_type == "image" and "images" in result:
                images = result["images"]
                if isinstance(images, list) and images:
                    first_image = images[0]
                    if isinstance(first_image, dict):
                        return first_image.get("url", str(first_image))
                    return str(first_image)
            
            # 包含 videos 列表
            if result_type == "video" and "videos" in result:
                videos = result["videos"]
                if isinstance(videos, list) and videos:
                    first_video = videos[0]
                    if isinstance(first_video, dict):
                        return first_video.get("url", str(first_video))
                    return str(first_video)
        
        # 其他情况转换为字符串
        return str(result)
        
    except Exception as e:
        return f"Error: 提取结果失败 - {str(e)}"


def get_project_root() -> str:
    """
    获取项目根目录路径
    
    Returns:
        项目根目录的绝对路径
    """
    # 假设此文件在 scripts 目录下
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def get_config_path() -> str:
    """获取配置文件路径"""
    return os.path.join(get_project_root(), "config.yaml")


def get_prompt_path(filename: str) -> str:
    """
    获取提示词文件路径
    
    Args:
        filename: 提示词文件名
        
    Returns:
        提示词文件的绝对路径
    """
    return os.path.join(get_project_root(), "prompts", filename)


def get_output_dir() -> str:
    """获取输出目录路径"""
    output_dir = os.path.join(get_project_root(), "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
