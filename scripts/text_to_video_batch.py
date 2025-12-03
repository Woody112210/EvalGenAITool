#!/usr/bin/env python3
"""
文本转视频批处理脚本
使用通用处理框架进行批量视频生成
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


class TextToVideoProcessor(BaseProcessor):
    """文本转视频处理器"""
    
    def __init__(self, config_file=None):
        """初始化处理器"""
        script_dir = Path(__file__).parent.parent
        prompt_file = script_dir / "prompts" / "text2video_prompts.csv"
        super().__init__(
            task_type="text_to_video",
            prompt_file=prompt_file,
            output_prefix="text_to_video_results",
            config_file=config_file
        )
    
    def on_queue_update(self, update):
        """处理队列更新"""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                logger.debug(log.get("message", ""))
    
    def generate_video(self, model_path, prompt, extra_args=None):
        """
        生成视频
        
        Args:
            model_path: 模型路径
            prompt: 提示词
            extra_args: 额外参数
            
        Returns:
            生成的视频URL
        """
        arguments = {"prompt": prompt}
        if extra_args:
            arguments.update(extra_args)
        
        try:
            handler = fal_client.subscribe(
                model_path,
                arguments=arguments,
                with_logs=True,
                on_queue_update=self.on_queue_update,
            )
            result = handler
            
            # 提取URL
            url = extract_url_from_dict(result)
            if not url:
                logger.warning(f"未知的结果格式: {result}")
                return str(result)
            
            return url
        except Exception as e:
            logger.error(f"生成视频失败 [{model_path}]: {e}")
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
        return self.generate_video(model_path, prompt, params)
    
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
    processor = TextToVideoProcessor()
    success = processor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
