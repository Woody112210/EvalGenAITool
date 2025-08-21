import os
import pandas as pd
import fal_client
import yaml
import datetime

CONFIG_FILE = "./config.yaml"
PROMPT_FILE = "../prompts/image2image_prompts.csv" if os.path.exists("../prompts/image2image_prompts.csv") else "image2image_prompts.csv"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PROMPT_COLUMN = "prompt"
IMAGE_COLUMN = "image_path"

# 生成带时间戳的 output 文件名
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "../output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"image_to_image_results_{TIMESTAMP}.csv")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

def image_to_image(model_path, prompt, image_path, extra_args=None):
    arguments = {"prompt": prompt}
    image_url = fal_client.upload_file(image_path)
    arguments["image_url"] = image_url
    if extra_args:
        arguments.update(extra_args)
    handler = fal_client.submit(
        model_path,
        arguments=arguments
    )
    result = handler.get()
    # 提取生成结果链接（假设 result 里有 url 字段或 images 字段）
    if isinstance(result, dict):
        if "url" in result:
            return result["url"]
        elif "images" in result and isinstance(result["images"], list) and result["images"]:
            return result["images"][0]
    return str(result)

def main():
    config = load_config()
    os.environ["FAL_KEY"] = config.get("fal_key", "")
    models = config.get("image_to_image_models", {})
    if not os.environ.get("FAL_KEY"):
        print("请先在 config.yaml 里填写 fal_key！")
        return
    df = pd.read_csv(PROMPT_FILE)
    if PROMPT_COLUMN not in df.columns or IMAGE_COLUMN not in df.columns:
        print(f"文件中未找到 '{PROMPT_COLUMN}' 或 '{IMAGE_COLUMN}' 列！")
        return
    total = len(df)
    results = []
    for idx, row in df.iterrows():
        prompt = row[PROMPT_COLUMN]
        image_path = row[IMAGE_COLUMN]
        row_result = {PROMPT_COLUMN: prompt, IMAGE_COLUMN: image_path}
        print(f"\n===== 正在处理第 {idx+1}/{total} 条 prompt =====")
        print(f"Prompt: {prompt}")
        print(f"Image: {image_path}")
        for model_name, model_info in models.items():
            model_path = model_info.get("model_path")
            params = model_info.get("params", {})
            print(f"  -> [{model_name}] 开始生成...")
            try:
                result_url = image_to_image(model_path, prompt, image_path, params)
                row_result[model_name] = result_url
                print(f"  -> [{model_name}] 生成完成！链接: {result_url}")
            except Exception as e:
                row_result[model_name] = f"Error: {e}"
                print(f"  -> [{model_name}] 生成出错: {e}")
        results.append(row_result)
        print(f"===== 第 {idx+1}/{total} 条 prompt 处理完成 =====\n")
    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_FILE, index=False)
    print(f"批量测试完成，结果已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
