"""
通用批处理基类
为所有批处理脚本提供统一的处理框架
"""
import os
import pandas as pd
import fal_client
from pathlib import Path
from datetime import datetime
from .logger_config import setup_logger
from .config_manager import ConfigManager
from .utils import ensure_output_dir, extract_url_from_dict

logger = setup_logger(__name__)


class BaseProcessor:
    """批处理基类"""
    
    def __init__(self, task_type, prompt_file, output_prefix, config_file=None):
        """
        初始化处理器
        
        Args:
            task_type: 任务类型 (text_to_image, text_to_video, image_to_image, image_to_video)
            prompt_file: 提示词文件路径
            output_prefix: 输出文件前缀
            config_file: 配置文件路径
        """
        self.task_type = task_type
        self.prompt_file = Path(prompt_file)
        self.output_prefix = output_prefix
        self.config_manager = ConfigManager(config_file)
        
        # 设置输出目录
        script_dir = Path(__file__).parent.parent
        self.output_dir = ensure_output_dir(script_dir / "output")
        
        # 生成时间戳和输出文件名
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = self.output_dir / f"{output_prefix}_{self.timestamp}.csv"
        
        # 设置API密钥
        api_key = self.config_manager.get_fal_key()
        os.environ["FAL_KEY"] = api_key
        
        # 获取模型配置
        self.models = self.config_manager.get_models(task_type)
        
        if not self.config_manager.validate_models(self.models):
            raise ValueError(f"模型配置验证失败")
        
        logger.info(f"初始化 {task_type} 处理器，模型数: {len(self.models)}")
    
    def load_prompts(self, prompt_column="prompt"):
        """
        加载提示词文件
        
        Args:
            prompt_column: 提示词列名
            
        Returns:
            DataFrame对象
        """
        if not self.prompt_file.exists():
            logger.error(f"提示词文件不存在: {self.prompt_file}")
            raise FileNotFoundError(f"提示词文件不存在: {self.prompt_file}")
        
        try:
            df = pd.read_csv(self.prompt_file)
            if prompt_column not in df.columns:
                logger.error(f"文件中未找到 '{prompt_column}' 列")
                raise ValueError(f"文件中未找到 '{prompt_column}' 列")
            
            logger.info(f"成功加载 {len(df)} 条提示词")
            return df
        except Exception as e:
            logger.error(f"加载提示词文件失败: {e}")
            raise
    
    def process_batch(self, df, process_func, prompt_column="prompt", extra_columns=None):
        """
        批量处理数据
        
        Args:
            df: 输入DataFrame
            process_func: 处理函数，接收(row, model_name, model_info)并返回结果
            prompt_column: 提示词列名
            extra_columns: 额外需要保留的列名列表
            
        Returns:
            结果列表
        """
        total = len(df)
        results = []
        
        logger.info(f"开始处理 {total} 条数据，使用 {len(self.models)} 个模型")
        
        for idx, row in df.iterrows():
            row_result = {}
            
            # 保留原始列
            row_result[prompt_column] = row[prompt_column]
            if extra_columns:
                for col in extra_columns:
                    if col in row.index:
                        row_result[col] = row[col]
            
            logger.info(f"处理第 {idx+1}/{total} 条数据")
            
            # 为每个模型生成结果
            for model_name, model_info in self.models.items():
                model_path = model_info.get("model_path")
                params = model_info.get("params", {})
                
                logger.debug(f"  [{model_name}] 开始处理")
                
                try:
                    result = process_func(row, model_name, model_info)
                    row_result[model_name] = result
                    logger.debug(f"  [{model_name}] 处理完成")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    row_result[model_name] = error_msg
                    logger.error(f"  [{model_name}] 处理失败: {e}")
            
            results.append(row_result)
        
        return results
    
    def save_results(self, results):
        """
        保存结果到CSV文件
        
        Args:
            results: 结果列表
        """
        try:
            df = pd.DataFrame(results)
            df.to_csv(self.output_file, index=False, encoding='utf-8')
            logger.info(f"结果已保存到: {self.output_file}")
            return self.output_file
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            raise
    
    def get_success_rate(self, results, model_name):
        """
        计算成功率
        
        Args:
            results: 结果列表
            model_name: 模型名称
            
        Returns:
            (成功数, 总数, 成功率百分比)
        """
        total = len(results)
        success_count = 0
        
        for result in results:
            value = result.get(model_name, "")
            if not str(value).startswith("Error:"):
                success_count += 1
        
        success_rate = (success_count / total * 100) if total > 0 else 0
        return success_count, total, success_rate
    
    def log_summary(self, results):
        """
        记录处理摘要
        
        Args:
            results: 结果列表
        """
        logger.info("=" * 50)
        logger.info("处理摘要")
        logger.info("=" * 50)
        
        for model_name in self.models.keys():
            success_count, total, success_rate = self.get_success_rate(results, model_name)
            logger.info(f"{model_name}: {success_count}/{total} ({success_rate:.1f}%)")
        
        logger.info("=" * 50)
