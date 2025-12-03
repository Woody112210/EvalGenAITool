#!/usr/bin/env python3
"""
结果解析脚本
将CSV结果转换为JSON格式用于Web展示
"""
import sys
import json
import argparse
from pathlib import Path

import pandas as pd

from lib.logger_config import setup_logger
from lib.utils import extract_url_from_result, is_valid_csv_file

logger = setup_logger(__name__)


def parse_csv_results(csv_file, output_file=None):
    """
    解析CSV结果文件
    
    Args:
        csv_file: CSV文件路径
        output_file: 输出JSON文件路径（可选）
        
    Returns:
        解析后的结果列表
    """
    csv_path = Path(csv_file)
    
    # 验证文件
    if not is_valid_csv_file(csv_file):
        raise ValueError(f"无效的CSV文件: {csv_file}")
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"成功加载CSV文件，共 {len(df)} 行")
    except Exception as e:
        logger.error(f"加载CSV文件失败: {e}")
        raise
    
    # 检查必要列
    if 'prompt' not in df.columns:
        logger.error("CSV文件中未找到 'prompt' 列")
        raise ValueError("CSV文件中未找到 'prompt' 列")
    
    results = []
    
    for idx, row in df.iterrows():
        prompt = row['prompt']
        result_item = {
            'id': idx + 1,
            'prompt': prompt,
        }
        
        # 提取所有模型的URL
        for col in df.columns:
            if col != 'prompt' and col != 'image_path':
                url = extract_url_from_result(row.get(col, ''))
                result_item[f'{col}_url'] = url
        
        results.append(result_item)
    
    logger.info(f"成功解析 {len(results)} 条结果")
    
    # 保存为JSON（如果指定了输出文件）
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"结果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            raise
    
    return results


def print_summary(results):
    """
    打印结果摘要
    
    Args:
        results: 结果列表
    """
    logger.info("=" * 60)
    logger.info("解析摘要")
    logger.info("=" * 60)
    logger.info(f"总条数: {len(results)}")
    
    # 统计各模型的成功率
    if results:
        model_stats = {}
        for result in results:
            for key, value in result.items():
                if key.endswith('_url') and key != 'id' and key != 'prompt':
                    model_name = key.replace('_url', '')
                    if model_name not in model_stats:
                        model_stats[model_name] = {'success': 0, 'total': 0}
                    model_stats[model_name]['total'] += 1
                    if value:
                        model_stats[model_name]['success'] += 1
        
        for model_name, stats in model_stats.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            logger.info(f"{model_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    logger.info("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='解析生成AI工具的CSV结果文件')
    parser.add_argument('csv_file', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出JSON文件路径', default=None)
    
    args = parser.parse_args()
    
    try:
        results = parse_csv_results(args.csv_file, args.output)
        print_summary(results)
        return 0
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
