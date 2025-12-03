"""
图像生成视频批处理脚本
支持多个模型并行测试，结果保存为 CSV 文件
"""

import os
import datetime
import pandas as pd
import fal_client
from typing import Dict, Any

from utils import (
    setup_logging,
    load_config,
    validate_api_key,
    extract_result_url,
    get_config_path,
    get_prompt_path,
    get_output_dir,
    get_project_root
)

# 设置日志
logger = setup_logging(__name__)

# 配置常量
PROMPT_COLUMN = "prompt"
IMAGE_COLUMN = "image_path"


def on_queue_update(update):
    """处理队列更新回调"""
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            logger.debug(f"  {log['message']}")


def image_to_video(model_path: str, prompt: str, image_path: str, extra_args: Dict[str, Any] = None) -> str:
    """
    图像生成视频并返回 URL 字符串
    
    Args:
        model_path: 模型路径
        prompt: 提示词
        image_path: 输入图像路径
        extra_args: 额外参数
        
    Returns:
        生成的视频 URL
        
    Raises:
        Exception: 生成失败时抛出异常
    """
    # 处理相对路径
    if not os.path.isabs(image_path):
        image_path = os.path.join(get_project_root(), image_path)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    try:
        # 上传图像文件
        image_url = fal_client.upload_file(image_path)
        logger.debug(f"图像已上传: {image_url}")
        
        # 构建参数
        arguments = {"prompt": prompt, "image_url": image_url}
        if extra_args:
            arguments.update(extra_args)
        
        # 提交任务
        result = fal_client.subscribe(
            model_path,
            arguments=arguments,
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        
        return extract_result_url(result, result_type="video")
        
    except Exception as e:
        logger.error(f"生成视频失败 [{model_path}]: {e}")
        raise


def main():
    """主函数"""
    try:
        # 加载配置
        config_path = get_config_path()
        config = load_config(config_path)
        
        # 设置 API 密钥
        fal_key = config.get("fal_key", "")
        if not validate_api_key(fal_key):
            logger.error("请先在 config.yaml 里填写有效的 fal_key！")
            logger.error("提示：请将占位符替换为您的实际 API 密钥")
            return
        
        os.environ["FAL_KEY"] = fal_key
        
        # 获取模型配置
        models = config.get("image_to_video_models", {})
        if not models:
            logger.error("config.yaml 中未找到 image_to_video_models 配置！")
            return
        
        # 加载提示词文件
        prompt_file = get_prompt_path("image2video_prompts.csv")
        if not os.path.exists(prompt_file):
            logger.error(f"提示词文件未找到: {prompt_file}")
            return
        
        df = pd.read_csv(prompt_file)
        if PROMPT_COLUMN not in df.columns or IMAGE_COLUMN not in df.columns:
            logger.error(f"文件中未找到 '{PROMPT_COLUMN}' 或 '{IMAGE_COLUMN}' 列！")
            return
        
        # 生成输出文件路径
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(get_output_dir(), f"image_to_video_results_{timestamp}.csv")
        
        total = len(df)
        results = []
        
        logger.info(f"开始处理 {total} 个提示词，使用 {len(models)} 个模型")
        logger.info(f"模型列表: {', '.join(models.keys())}")
        
        # 处理每个提示词
        for idx, row in df.iterrows():
            prompt = row[PROMPT_COLUMN]
            image_path = row[IMAGE_COLUMN]
            row_result = {PROMPT_COLUMN: prompt, IMAGE_COLUMN: image_path}
            
            logger.info(f"\n{'='*60}")
            logger.info(f"正在处理第 {idx+1}/{total} 条 prompt")
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Image: {image_path}")
            logger.info(f"{'='*60}")
            
            # 对每个模型生成视频
            for model_name, model_info in models.items():
                model_path = model_info.get("model_path")
                params = model_info.get("params", {})
                
                if not model_path:
                    logger.warning(f"模型 {model_name} 缺少 model_path 配置")
                    row_result[model_name] = "Error: Missing model_path"
                    continue
                
                logger.info(f"  -> [{model_name}] 开始生成...")
                try:
                    result_url = image_to_video(model_path, prompt, image_path, params)
                    row_result[model_name] = result_url
                    logger.info(f"  -> [{model_name}] 生成完成！")
                    logger.debug(f"     URL: {result_url}")
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    row_result[model_name] = error_msg
                    logger.error(f"  -> [{model_name}] 生成出错: {e}")
            
            results.append(row_result)
            logger.info(f"第 {idx+1}/{total} 条 prompt 处理完成\n")
        
        # 保存结果
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"\n批量测试完成，结果已保存到: {output_file}")
        
        # 统计成功率
        logger.info("\n=== 生成统计 ===")
        for model_name in models.keys():
            if model_name in result_df.columns:
                success_count = sum(
                    1 for val in result_df[model_name] 
                    if not str(val).startswith("Error:")
                )
                success_rate = (success_count / total) * 100
                logger.info(f"{model_name}: {success_count}/{total} ({success_rate:.1f}%)")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
