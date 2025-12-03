#!/usr/bin/env python3
"""
文本转图像批处理脚本
使用通用处理框架进行批量图像生成
"""
import sys
from pathlib import Path

# 添加lib目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import fal_client
from lib.base_processor import BaseProcessor
from lib.logger_config import setup_logger
from lib.utils import extract_url_from_dict

logger = setup_logger(__name__)


class TextToImageProcessor(BaseProcessor):
    """文本转图像处理器"""
    
    def __init__(self, config_file=None):
        """初始化处理器"""
        script_dir = Path(__file__).parent.parent
        prompt_file = script_dir / "prompts" / "text2image_prompts.csv"
        super().__init__(
            task_type="text_to_image",
            prompt_file=prompt_file,
            output_prefix="text_to_image_results",
            config_file=config_file
        )
    
    def generate_image(self, model_path, prompt, extra_args=None):
        """
        生成图像
        
        Args:
            model_path: 模型路径
            prompt: 提示词
            extra_args: 额外参数
            
        Returns:
            生成的图像URL
        """
        arguments = {"prompt": prompt}
        if extra_args:
            arguments.update(extra_args)
        
        try:
            handler = fal_client.submit(model_path, arguments=arguments)
            result = handler.get()
            
            # 提取URL
            url = extract_url_from_dict(result)
            if not url:
                logger.warning(f"未知的结果格式: {result}")
                return str(result)
            
            return url
        except Exception as e:
            logger.error(f"生成图像失败 [{model_path}]: {e}")
            raise
    
    def process_row(self, row, model_name, model_info):
        """
        处理单行数据
        
        Args:
            row: 数据行
            model_name: 模型名称
            model_info: 模型信息
            
        Returns:
            生成结果
        """
        prompt = row["prompt"]
        model_path = model_info.get("model_path")
        params = model_info.get("params", {})
        
        logger.debug(f"处理提示词: {prompt}")
        return self.generate_image(model_path, prompt, params)
    
    def run(self):
        """运行处理流程"""
        try:
            # 加载提示词
            df = self.load_prompts(prompt_column="prompt")
            
            # 批量处理
            results = self.process_batch(
                df,
                self.process_row,
                prompt_column="prompt"
            )
            
            # 保存结果
            self.save_results(results)
            
            # 记录摘要
            self.log_summary(results)
            
            logger.info("处理完成")
            return True
        except Exception as e:
            logger.error(f"处理失败: {e}")
            return False


def main():
    """主函数"""
    processor = TextToImageProcessor()
    success = processor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
