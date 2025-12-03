"""
通用工具函数模块
"""
import os
import re
import ast
from pathlib import Path
from .logger_config import setup_logger

logger = setup_logger(__name__)


def ensure_output_dir(output_dir):
    """
    确保输出目录存在
    
    Args:
        output_dir: 输出目录路径
        
    Returns:
        输出目录路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def extract_url_from_result(result_str):
    """
    从结果字符串中提取URL
    
    Args:
        result_str: 结果字符串（可能是字典的字符串表示）
        
    Returns:
        提取的URL，如果无法提取则返回None
    """
    try:
        if isinstance(result_str, str):
            if result_str.startswith("Error:"):
                return None
            
            # 尝试作为字面量字典解析
            try:
                result_dict = ast.literal_eval(result_str)
                if isinstance(result_dict, dict):
                    return result_dict.get('url')
            except (ValueError, SyntaxError):
                pass
            
            # 尝试用正则表达式提取URL
            url_match = re.search(r"'url': '([^']+)'", result_str)
            if url_match:
                return url_match.group(1)
            
            # 尝试提取http/https URL
            url_match = re.search(r'https?://[^\s"\']+', result_str)
            if url_match:
                return url_match.group(0)
        
        return None
    except Exception as e:
        logger.warning(f"解析结果时出错: {e}")
        return None


def extract_url_from_dict(result_dict):
    """
    从结果字典中提取URL
    
    Args:
        result_dict: 结果字典
        
    Returns:
        提取的URL字符串
    """
    if isinstance(result_dict, dict):
        # 尝试直接获取url字段
        if "url" in result_dict:
            return result_dict["url"]
        
        # 尝试从images列表中获取
        if "images" in result_dict and isinstance(result_dict["images"], list):
            if result_dict["images"]:
                first_image = result_dict["images"][0]
                if isinstance(first_image, dict):
                    return first_image.get("url", str(first_image))
                return str(first_image)
        
        # 尝试从videos列表中获取
        if "videos" in result_dict and isinstance(result_dict["videos"], list):
            if result_dict["videos"]:
                first_video = result_dict["videos"][0]
                if isinstance(first_video, dict):
                    return first_video.get("url", str(first_video))
                return str(first_video)
    
    return str(result_dict) if result_dict else None


def format_file_path(base_dir, filename):
    """
    格式化文件路径
    
    Args:
        base_dir: 基础目录
        filename: 文件名
        
    Returns:
        完整的文件路径
    """
    return str(Path(base_dir) / filename)


def is_valid_csv_file(file_path):
    """
    检查CSV文件是否有效
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否有效
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return False
    
    if not file_path.suffix.lower() == '.csv':
        logger.error(f"文件不是CSV格式: {file_path}")
        return False
    
    return True
