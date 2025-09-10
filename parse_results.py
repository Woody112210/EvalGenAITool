#!/usr/bin/env python3
import pandas as pd
import json
import re
import ast

def extract_url_from_result(result_str):
    """Extract URL from the result string which contains a dictionary"""
    try:
        # Handle the case where result_str might be a string representation of a dict
        if isinstance(result_str, str):
            if result_str.startswith("Error:"):
                return None
            # Try to parse as literal dict
            try:
                result_dict = ast.literal_eval(result_str)
                return result_dict.get('url')
            except:
                # Try regex to extract URL
                url_match = re.search(r"'url': '([^']+)'", result_str)
                if url_match:
                    return url_match.group(1)
        return None
    except Exception as e:
        print(f"Error parsing result: {e}")
        return None

def parse_csv_results(csv_file):
    """Parse the CSV results and extract image data"""
    df = pd.read_csv(csv_file)
    
    results = []
    for idx, row in df.iterrows():
        prompt = row['prompt']
        
        # Extract URLs for each model
        hunyuan_url = extract_url_from_result(row.get('hunyuan', ''))
        flux_url = extract_url_from_result(row.get('flux', ''))
        
        result_item = {
            'id': idx + 1,
            'prompt': prompt,
            'hunyuan_url': hunyuan_url,
            'flux_url': flux_url
        }
        results.append(result_item)
    
    return results

def main():
    # Parse the latest results
    csv_file = '/home/ubuntu/EvalGenAITool/output/text_to_image_results_20250910_064833.csv'
    results = parse_csv_results(csv_file)
    
    # Save as JSON for web page
    output_file = '/home/ubuntu/EvalGenAITool/image_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Parsed {len(results)} results and saved to {output_file}")
    
    # Print summary
    hunyuan_success = sum(1 for r in results if r['hunyuan_url'])
    flux_success = sum(1 for r in results if r['flux_url'])
    
    print(f"Hunyuan successful generations: {hunyuan_success}/{len(results)}")
    print(f"Flux successful generations: {flux_success}/{len(results)}")

if __name__ == "__main__":
    main()
