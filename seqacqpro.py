import sys
import gzip

def load_genome(genome_file):
    """加载基因组文件，返回染色体序列字典"""
    genome = {}
    current_chr = None
    seq = []
    
    open_func = gzip.open if genome_file.endswith('.gz') else open
    
    with open_func(genome_file, 'rt') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_chr:
                    genome[current_chr] = ''.join(seq)
                current_chr = line[1:].split()[0]  # 取>后的第一个单词作为染色体名
                seq = []
            else:
                seq.append(line.upper())
        if current_chr:
            genome[current_chr] = ''.join(seq)
    return genome

def extract_promoter(gene_file, genome, promoter_size=2000):
    """从基因区间文件中提取启动子序列"""
    with open(gene_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) < 6 or parts[1] != 'gene':
                continue
             
            chrom = parts[0]
            start = int(parts[2])
            end = int(parts[3])
            strand = parts[4]
            gene_id = parts[5].strip('";')
            print("run!")
            if chrom not in genome:
                print(f"Warning: Chromosome {chrom} not found in genome", file=sys.stderr)
                continue
            
            # 计算启动子区域
            if strand == '+':
                prom_start = max(1, start - promoter_size)
                prom_end = start - 1
                promoter_seq = genome[chrom][prom_start-1:prom_end]
            else:
                prom_start = end + 1
                prom_end = end + promoter_size
                promoter_seq = reverse_complement(genome[chrom][prom_start-1:prom_end])
            
            # 输出FASTA格式
            print(f">{gene_id}|promoter_{prom_start}_{prom_end}|{chrom}:{start}-{end}({strand})")
            print(break_lines(promoter_seq))

def reverse_complement(seq):
    """返回反向互补序列"""
    comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join(comp[base] for base in reversed(seq))

def break_lines(seq, line_length=80):
    """将长序列分割为多行"""
    return '\n'.join(seq[i:i+line_length] for i in range(0, len(seq), line_length))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <gene_interval_file> <genome_file>", file=sys.stderr)
        sys.exit(1)
    
    gene_file = sys.argv[1]
    genome_file = sys.argv[2]
    
    intervalsize = int(sys.argv[3])
   
    genome = load_genome(genome_file)
    extract_promoter(gene_file, genome,intervalsize)
