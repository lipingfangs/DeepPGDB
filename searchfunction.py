from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import argparse
import re
import os


def find_fuzzy_matches(filename, keyword, threshold=70, show_score=False):
    """
    在文件中查找与关键词模糊匹配的行
    
    参数:
        filename (str): 要搜索的文件路径
        keyword (str): 要匹配的关键词
        threshold (int): 匹配阈值(0-100)，默认70
        show_score (bool): 是否显示匹配分数
    """
    try:
        with open(filename, 'r',errors='ignore') as file:
            lines = file.readlines()
        
    #    print(f"在文件 '{filename}' 中搜索模糊匹配 '{keyword}' (阈值={threshold})...\n")
        
        matches = []
        for line in lines:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            
            # 计算相似度分数
            score = fuzz.partial_ratio(line.lower(), keyword.lower())
            
                #line = re.findall(r'\b\w+\b', line.lower())
               # best_match = process.extractOne(line, keyword.lower(), scorer=fuzz.ratio)
              #  score = fuzz.ratio(line.lower(), keyword.lower())
            
            if score >= threshold:
                matches.append((line, score))
        
        # 按匹配分数排序
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if matches:
    #        print(f"找到 {len(matches)} 个匹配:")
            for line, score in matches:
                if show_score:
                    print(f"[{score}] {line}")
                else:
                    print(line)
        else:
            print("未找到匹配的行。")
            
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}' 未找到。")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="在文件中模糊搜索关键词")
    parser.add_argument("filename", help="要搜索的文件路径")
    parser.add_argument("keyword", help="要搜索的关键词")
    parser.add_argument("-t", "--threshold", type=int, default=75, 
                       help="匹配阈值(0-100)，默认75")
    parser.add_argument("-s", "--show-score", action="store_true",
                       help="显示匹配分数")
    
    args = parser.parse_args()
    if args.threshold > 99:
        command = f"cat {args.filename} | grep -w '{args.keyword}' "
        print(command)
        os.system(command)
    else:   
        find_fuzzy_matches(args.filename, args.keyword, 
                      threshold=args.threshold, 
                      show_score=args.show_score)

