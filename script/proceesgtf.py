import sys
import re

def process_gtf(input_file):
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                print(line.strip())
                continue
            
            fields = line.strip().split('\t')
        #    print(fields)
            if len(fields) < 8:
                continue
            
            # 提取需要的列
            selected_cols = [fields[0], fields[2], fields[3], fields[4], fields[6]]
            
            # 处理最后一列
            last_col = fields[8]
            gene_id = re.search(r'gene_id "([^"]+)"', last_col)
            transcript_id = re.search(r'transcript_id "([^"]+)"', last_col)
            gene_name = re.search(r'gene_name "([^"]+)"', last_col)
            
            # 构建新的最后一列
            new_last_col = []
            if gene_id:
                new_last_col.append(f'gene_id "{gene_id.group(1)}"')
            if transcript_id:
                new_last_col.append(f'transcript_id "{transcript_id.group(1)}"')
            if gene_name:
                new_last_col.append(f'gene_name "{gene_name.group(1)}"')
            else:
                # 如果没有gene_name，使用gene_id作为gene_name
                if gene_id:
                    new_last_col.append(f'gene_name "{gene_id.group(1)}"')
            
            # 合并所有列
            output_line = '\t'.join(selected_cols + ['; '.join(new_last_col)])
            print(output_line)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py input.gtf")
        sys.exit(1)
    input_file = sys.argv[1]
    process_gtf(input_file) 
