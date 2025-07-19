import sys
import os 

def process_fasta(input_file, output_file):
    """
    处理FASTA格式文件，将多行序列合并为单行
    
    参数:
        input_file (str): 输入FASTA文件路径
        output_file (str): 输出处理后的FASTA文件路径
    """
    # 第一步：处理原始文件，将序列行合并
    with open(input_file, "r") as file1:
        lines = file1.readlines()
    
    with open("temp2020818", "w") as file2:
        for line in lines:
            line = line.strip()
            if line.startswith(">"):
                print("", file=file2)  # 添加空行分隔不同序列
                print(line, file=file2)
            else:
                print(line, end="", file=file2)
    
    # 第二步：移除临时文件中的空行并写入最终输出
    with open("temp2020818", "r") as file3, open(output_file, "w") as file4:
        for line in file3.readlines()[1:]:  # 跳过第一行空行
            line = line.strip()
            if line:  # 只写入非空行
                print(line, file=file4)
    
    # 删除临时文件
    os.remove("temp2020818")
                               
    
def addspinfo(input_filename,output_filename, speicesname,commonname):
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        for line in infile:
            if line.startswith("你是一个由华南农业大学"):
                insert_pos = line.find(",输出时大小写不能有变化")
                if insert_pos != -1:
                    line = line[:insert_pos] +"," + dicinfo["SpeicesName"]+"为"+dicinfo["CommonName"]+ line[insert_pos:]    
                    print(line)

            outfile.write(line)
                    
                

getinfofile = open(sys.argv[1],"r")
getinfofileline=getinfofile.readlines()
getinfofile.close()

dicinfo={}
for i in getinfofileline:
    i = i.strip().split("=")
    dicinfo[i[0]] = i[1]

process_fasta(dicinfo["Genome"],dicinfo["SpeicesName"]+"."+"genome")
process_fasta(dicinfo["cds"],dicinfo["SpeicesName"]+".genome."+"cds")
process_fasta(dicinfo["pep"],dicinfo["SpeicesName"]+".genome."+"pep")
process_fasta(dicinfo["cdna"],dicinfo["SpeicesName"]+".genome."+"cdna")
addspinfo(dicinfo["inputinfofile"],dicinfo["outinfofile"],dicinfo["SpeicesName"],dicinfo["CommonName"])

os.system("cat "+ dicinfo["SpeicesName"]+"."+"genome.cdna"+" "+dicinfo["SpeicesName"]+"."+"genome.cds"+" "+dicinfo["SpeicesName"]+"."+"genome.pep"+" > "+" "+dicinfo["SpeicesName"]+"."+"genome.gene")
os.system("makeblastdb -in "+ dicinfo["SpeicesName"]+"."+"genome" + " -dbtype nucl")

print("makeblastdb -in "+ dicinfo["SpeicesName"]+"."+"genome" + " -dbtype nucl")
os.system("makeblastdb -in "+ dicinfo["SpeicesName"]+"."+"genome.pep" + " -dbtype prot")
os.system("makeblastdb -in "+ dicinfo["SpeicesName"]+"."+"genome.cds" + " -dbtype nucl -out "+ dicinfo["SpeicesName"]+"."+"genome.cds")
os.system("cp "+dicinfo["functioninfo"]+" "+dicinfo["SpeicesName"]+"."+"genome.ann")

