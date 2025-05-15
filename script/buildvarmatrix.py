def combine_ped_map(ped_file, map_file, output_file):
    # 读取MAP文件，提取变异位点ID
    variant_ids = []
    with open(map_file, 'r') as map_f:
        for line in map_f:
            parts = line.strip().split()
            variant_id = parts[0]+"_"+parts[3]  # 第二列是变异位点ID
            variant_ids.append(variant_id)
    
    # 读取PED文件，提取样本ID和基因型数据
    samples = []
    genotypes = []
    with open(ped_file, 'r') as ped_f:
        for line in ped_f:
            parts = line.strip().split()
            sample_id = parts[0]  # 第一列是样本ID
            samples.append(sample_id)
            
            # 从第7列开始是基因型数据
            genotype_data = parts[6:]
            # 将每两个等位基因合并为一个基因型
            genotype = []
            for i in range(0, len(genotype_data), 2):
                allele1 = genotype_data[i]
                allele2 = genotype_data[i+1]
                genotype.append(allele1 + allele2)
            genotypes.append(genotype)
    
    # 写入CSV文件
    with open(output_file, 'w') as out_f:
        # 写入表头（样本ID + 变异位点ID）
        header = ['SampleID'] + variant_ids
        out_f.write(','.join(header) + '\n')
        
        # 写入每个样本的基因型数据
        for sample, genotype in zip(samples, genotypes):
            row = [sample] + genotype
            out_f.write(','.join(row) + '\n')
    
    print(f"结果已保存到 {output_file}")

# 示例调用
import sys
ped_file = sys.argv[1]  # 替换为你的PED文件路径
map_file = sys.argv[2]  # 替换为你的MAP文件路径
output_file = 'output_genotypes.csv'  # 输出文件路径
combine_ped_map(ped_file, map_file, output_file)
