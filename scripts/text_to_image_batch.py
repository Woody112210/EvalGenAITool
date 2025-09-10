import os
import pandas as pd
import fal_client
import yaml
import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 修复路径问题 - 使用相对于脚本文件的路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "../config.yaml")
PROMPT_FILE = os.path.join(SCRIPT_DIR, "../prompts/text2image_prompts.csv")

PROMPT_COLUMN = "prompt"

# 生成带时间戳的 output 文件名
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "../output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"text_to_image_results_{TIMESTAMP}.csv")

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {CONFIG_FILE}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise

def generate_image(model_path, prompt, extra_args=None):
    """生成图像并返回URL字符串"""
    arguments = {"prompt": prompt}
    if extra_args:
        arguments.update(extra_args)
    
    try:
        handler = fal_client.submit(model_path, arguments=arguments)
        result = handler.get()
        
        # 简化结果提取 - 直接返回URL字符串
        if isinstance(result, dict):
            if "url" in result:
                return result["url"]
            elif "images" in result and isinstance(result["images"], list) and result["images"]:
                first_image = result["images"][0]
                if isinstance(first_image, dict):
                    return first_image.get("url", str(first_image))
                return str(first_image)
        
        logger.warning(f"未知的结果格式: {result}")
        return str(result)
        
    except Exception as e:
        logger.error(f"生成图像失败 [{model_path}]: {e}")
        raise

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        os.environ["FAL_KEY"] = config.get("fal_key", "")
        models = config.get("text_to_image_models", {})
        
        # 验证API密钥
        if not os.environ.get("FAL_KEY") or os.environ.get("FAL_KEY") == "YOUR_API_KEY_HERE":
            logger.error("请先在 config.yaml 里填写有效的 fal_key！")
            return
        
        # 验证模型配置
        if not models:
            logger.error("config.yaml 中未找到 text_to_image_models 配置！")
            return
        
        # 加载提示词文件
        if not os.path.exists(PROMPT_FILE):
            logger.error(f"提示词文件未找到: {PROMPT_FILE}")
            return
            
        df = pd.read_csv(PROMPT_FILE)
        if PROMPT_COLUMN not in df.columns:
            logger.error(f"文件中未找到 '{PROMPT_COLUMN}' 列！")
            return
        
        total = len(df)
        results = []
        
        logger.info(f"开始处理 {total} 个提示词，使用 {len(models)} 个模型")
        
        for idx, row in df.iterrows():
            prompt = row[PROMPT_COLUMN]
            row_result = {PROMPT_COLUMN: prompt}
            
            print(f"\n===== 正在处理第 {idx+1}/{total} 条 prompt =====")
            print(f"Prompt: {prompt}")
            
            for model_name, model_info in models.items():
                model_path = model_info.get("model_path")
                params = model_info.get("params", {})
                
                if not model_path:
                    logger.warning(f"模型 {model_name} 缺少 model_path 配置")
                    row_result[model_name] = "Error: Missing model_path"
                    continue
                
                print(f"  -> [{model_name}] 开始生成...")
                try:
                    result_url = generate_image(model_path, prompt, params)
                    row_result[model_name] = result_url
                    print(f"  -> [{model_name}] 生成完成！链接: {result_url}")
                except Exception as e:
                    row_result[model_name] = f"Error: {e}"
                    print(f"  -> [{model_name}] 生成出错: {e}")
            
            results.append(row_result)
            print(f"===== 第 {idx+1}/{total} 条 prompt 处理完成 =====\n")
        
        # 保存结果
        result_df = pd.DataFrame(results)
        result_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        logger.info(f"批量测试完成，结果已保存到 {OUTPUT_FILE}")
        
        # 统计成功率
        for model_name in models.keys():
            if model_name in result_df.columns:
                success_count = sum(1 for val in result_df[model_name] if not str(val).startswith("Error:"))
                logger.info(f"{model_name} 成功率: {success_count}/{total}")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise

if __name__ == "__main__":
    main()
