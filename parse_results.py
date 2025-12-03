#!/usr/bin/env python3
"""
结果解析脚本
从 CSV 结果文件中提取图像 URL，保存为 JSON 格式
"""

import os
import sys
import pandas as pd
import json
import re
import ast
from typing import Optional, Dict, Any, List


def extract_url_from_result(result_str: Any) -> Optional[str]:
    """
    从结果字符串中提取 URL
    
    Args:
        result_str: 结果字符串或字典
        
    Returns:
        提取的 URL，失败时返回 None
    """
    try:
        # 处理空值
        if pd.isna(result_str) or result_str is None:
            return None
        
        # 如果是字符串
        if isinstance(result_str, str):
            # 跳过错误信息
            if result_str.startswith("Error:"):
                return None
            
            # 如果已经是 URL
            if result_str.startswith("http://") or result_str.startswith("https://"):
                return result_str
            
            # 尝试解析为字典
            try:
                result_dict = ast.literal_eval(result_str)
                if isinstance(result_dict, dict):
                    return result_dict.get('url')
            except (ValueError, SyntaxError):
                pass
            
            # 使用正则表达式提取 URL
            url_match = re.search(r"'url':\s*'([^']+)'", result_str)
            if url_match:
                return url_match.group(1)
            
            # 尝试直接匹配 URL 模式
            url_match = re.search(r'https?://[^\s\'"]+', result_str)
            if url_match:
                return url_match.group(0)
        
        # 如果是字典
        elif isinstance(result_str, dict):
            return result_str.get('url')
        
        return None
        
    except Exception as e:
        print(f"解析结果时出错: {e}")
        return None


def parse_csv_results(csv_file: str, model_columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    解析 CSV 结果文件并提取数据
    
    Args:
        csv_file: CSV 文件路径
        model_columns: 模型列名列表，如果为 None 则自动检测
        
    Returns:
        解析后的结果列表
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"文件不存在: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # 自动检测模型列（排除 prompt 和 image_path 列）
    if model_columns is None:
        excluded_columns = {'prompt', 'image_path'}
        model_columns = [col for col in df.columns if col not in excluded_columns]
    
    results = []
    for idx, row in df.iterrows():
        result_item = {
            'id': idx + 1,
            'prompt': row.get('prompt', ''),
        }
        
        # 如果有图像路径列，也包含进来
        if 'image_path' in row:
            result_item['image_path'] = row['image_path']
        
        # 提取每个模型的 URL
        for model_name in model_columns:
            if model_name in row:
                url = extract_url_from_result(row[model_name])
                result_item[f'{model_name}_url'] = url
        
        results.append(result_item)
    
    return results


def print_summary(results: List[Dict[str, Any]], model_columns: List[str]):
    """
    打印统计摘要
    
    Args:
        results: 结果列表
        model_columns: 模型列名列表
    """
    total = len(results)
    print(f"\n解析了 {total} 条结果")
    print("\n=== 成功率统计 ===")
    
    for model_name in model_columns:
        url_key = f'{model_name}_url'
        success_count = sum(1 for r in results if r.get(url_key))
        success_rate = (success_count / total * 100) if total > 0 else 0
        print(f"{model_name}: {success_count}/{total} ({success_rate:.1f}%)")


def main():
    """主函数"""
    # 默认使用最新的结果文件
    default_csv = '/home/ubuntu/EvalGenAITool/output/text_to_image_results_20250910_064833.csv'
    
    # 如果提供了命令行参数，使用指定的文件
    csv_file = sys.argv[1] if len(sys.argv) > 1 else default_csv
    
    # 输出文件路径
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/home/ubuntu/EvalGenAITool/image_results.json'
    
    try:
        print(f"正在解析文件: {csv_file}")
        
        # 解析结果
        results = parse_csv_results(csv_file)
        
        # 自动检测模型列
        if results:
            model_columns = [
                key.replace('_url', '') 
                for key in results[0].keys() 
                if key.endswith('_url')
            ]
        else:
            model_columns = []
        
        # 保存为 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"结果已保存到: {output_file}")
        
        # 打印统计信息
        print_summary(results, model_columns)
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
