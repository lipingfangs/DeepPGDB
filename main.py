from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import re
import subprocess
import json
from collections import defaultdict
import math
import tiktoken
import time

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 模型 API 的地址
MODEL_API_URL = "http://RiceGenomicHJX.xiaomy.net:11058/api/generate"

# 使用字典存储每个用户的对话历史，键为 Session ID
conversation_histories = defaultdict(list)

# 存储每个用户上一次的 cleaned_output
last_cleaned_outputs = {}

# 预先激励的提示
pre_promptfile = open("./prompt6.txt","r")
pre_prompt = pre_promptfile.read()
pre_promptfile.close()

pre_prompt2="请根据以下文档回答用户问题,如果用户用英语提问,则用英语回答："




def count_think_tokens(text: str, model: str = "gpt-4") -> int:
    """
    计算文本中 <think> 标签内容的 token 数量
    
    Args:
        text (str): 包含 <think> 标签的文本
        model (str): 使用的模型（默认 "gpt-4"）
    
    Returns:
        int: <think> 内容的 token 数量，如果不存在则返回 0
    """
    # 提取 <think> 标签内容
    start_tag = "<think>"
    end_tag = "</think>"
    
    start_idx = text.find(start_tag)
    if start_idx == -1:
        return 0
    
    end_idx = text.find(end_tag, start_idx)
    if end_idx == -1:
        return 0
    
    think_content = text[start_idx + len(start_tag):end_idx].strip()
    
    # 初始化 tokenizer
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # 默认使用 gpt-4 的编码
    
    # 计算 token 数量
    tokens = encoding.encode(think_content)
    return len(tokens)

def cleangenelist(greporder):
    grepgene = greporder.split('"')[1].strip()
    speciesprm = greporder.split()[1].strip().split(".")
    species = speciesprm[0] + "." + speciesprm[1]
    print("Speices:",species)
    print("grepgene:",grepgene, "cat "+species +".id | grep  "+grepgene+" > tempifonlyone.gene")
    
    os.system("cat "+species+".id | grep  "+grepgene+" > tempifonlyone.gene")
    grepcontentfile =  open("tempifonlyone.gene","r")
    genelist = grepcontentfile.readlines()
    grepcontent = "<br>".join(genelist)
    grepcontentfile.close()
    print(grepcontent)
    targetgenelist = []
    for i in genelist:
        
        targetgenelist.append(i.split("\t")[0])
    targetgenelistclean = list(set(targetgenelist))
    print(targetgenelistclean)
    if len(targetgenelistclean) ==1:
        replacecommand = greporder.replace(grepgene,targetgenelistclean[0])
        return "only one :"+replacecommand
    else:
        #return grepcontent
        return "<br>".join(targetgenelistclean)

def csv_to_html_from_string(csv_content):
    # 将CSV内容按行分割
    rows = csv_content.strip().split('\n')
    
    # 开始构建HTML表格
    html = '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            text-align: center;
        }
        table th, table td {
            padding: 10px 12px;
            border: 1px solid #ddd;
        }
        table th {
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
           /* writing-mode: vertical-rl; /* 文字垂直排列 */*/

            transform: rotate(0deg); /* 文字旋转180度，使其从上到下阅读 */
            white-space: nowrap; /* 防止文字换行 */
        }
        table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        table tr:hover {
            background-color: #f1f1f1;
        }
    </style>
    <table>\n'
    '''
    
    # 遍历每一行
    for i, row in enumerate(rows):
        html += '  <tr>\n'
        # 将每一行的内容按逗号分割成单元格
        cells = row.split(',')
        # 如果是第一行，使用<th>标签表示表头
        tag = 'th' if i == 0 else 'td'
        for cell in cells:
            html += f'    <{tag}>{cell.strip()}</{tag}>'
        html += '  </tr>\n'
    
    html += '</table>'
    
    return html

def txt_to_html_from_string(csv_content):
    # 将CSV内容按行分割
    rows = csv_content.strip().split('\n')

    # 开始构建HTML表格
    html = '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            text-align: center;
        }
        table th, table td {
            padding: 10px 12px;
            border: 1px solid #ddd;
        }
        table th {
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
           /* writing-mode: vertical-rl; /* 文字垂直排列 */*/

            transform: rotate(0deg); /* 文字旋转180度，使其从上到下阅读 */
            white-space: nowrap; /* 防止文字换行 */

        }
        table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        table tr:hover {
            background-color: #f1f1f1;
        }
    </style>
    <table>\n'
    '''

    # 遍历每一行
    for i, row in enumerate(rows):
        html += '  <tr>\n'
        # 将每一行的内容按逗号分割成单元格
        cells = row.split('\t')
        # 如果是第一行，使用<th>标签表示表头
        tag = 'th' if i == 0 else 'td'
        for cell in cells:
            html += f'    <{tag}>{cell.strip()}</{tag}>'
        html += '  </tr>\n'

    html += '</table>'

    return html

def convertPointdata_to_echart_format(data):
    echarts_data = []
    x_data = []  # X 轴数据（倒数第三列）
    y_data = []  # Y 轴数据（-log10(倒数第二列)）
    size_data = []  # 点的大小（第二列）
    color_data = []  # 点的颜色（-log10(倒数第二列)）
    print(data.split("\n"))
    for line in data.split("\n"):
        if len(line) < 3:
           continue
        columns = line.strip().split()
        y_value = float(columns[-1])  # 倒数第二列的值
       
        # 筛选倒数第二列小于0.01的行
        if y_value < 0.00001:
            x_data.append(float(math.log10(float(columns[-3]))))  # X 轴数据
            log_y_value = -math.log10(y_value)  # 计算 -log10(y_value)
            y_data.append(log_y_value)  # Y 轴数据
            size_data.append(float(columns[1]))  # 点的大小
            color_data.append(log_y_value)  # 点的颜色

    # ECharts 配置
    echart_config = {
        "title": {
            "text": "GO Terms scatter"  # 标题
        },
        "tooltip": {
            "formatter": "function (params) { return 'GO ID: ' + params.data[0] + '<br>X: ' + params.data[1].toFixed(3) + '<br>Y: ' + params.data[2].toFixed(3); }"
        },
        "xAxis": {
            "name": "X Value",
            "type": "value",
            "scale": True
        },
        "yAxis": {
            "name": "-log10(Y Value)",
            "type": "value",
            "scale": True
        },
        "series": [{
            "name": "GO Terms Scatter",
            "type": "scatter",
            "data": [[x, y, size, color] for x, y, size, color in zip(x_data, y_data, size_data, color_data)],  # 数据格式: [X, Y, size, color]
            "symbolSize": 20,  # 点的大小
            "itemStyle": {
                "color": "#8B6914"
            }
        }]
    }
    outechart = json.dumps(echart_config, indent=4).replace('"function (data) {return data[2];}"',"function (data) {return data[2];}")
    return f"<echart>{outechart}</echart>"





import json
def population_hapcommand(model_output):
    if "#haplotype" in model_output:
        commands = "python halotypepie.py output_genotypes.previous.csv poplutaion.info"
        print("Executing command:", commands)
        os.system(commands.strip())
        #file_content = read_file_with_cat("haplotype_pie_chart.json")
        with open('haplotype_pie_chart.json', 'r', encoding='utf-8') as file:
    # 加载JSON数据
            echart_config = json.load(file)
         
       # happie = file_content.strip()
        print(echart_config)
        os.system("rm haplotype_pie_chart.json; rm output_genotypes.previous.csv")
        return f"<echart>{json.dumps(echart_config, indent=4)}</echart>"
    
def Protein_elecommand(model_output):
    if "#Protein" in model_output:
        commands = "python calculatepep.py --fasta tempgeneprevious.fa  --csv tempgeneprevious.fa.out"
        print("Executing command:", commands)
        os.system(commands.strip())
        os.system("tail -n 1 tempgeneprevious.fa.out |awk -F ',' '{print $1,$2,$3,$4,$5,$6,$7,$8}' > tempgeneprevious.fa.out.end")
        file_content = read_file_with_cat("tempgeneprevious.fa.out.end")
        
        pepinfo = "ID\tProtein Length\tCDS Length\tMolecular Weight (kDa)\tIsoelectric Point\tHydrophilicity\tAliphatic\tInstability\n" + file_content.replace(" ","\t")
        pepinfo  = txt_to_html_from_string(pepinfo)
        os.system("rm tempgeneprevious.fa; rm tempgeneprevious.fa.out")
       # return f"Had been Executed: <br><br> {commands} <br><br> The Protein information is: <br><br> {pepinfo}" 
        return f"The Protein properties is: <br> {pepinfo}" 
def getenrichment_command(model_output):
    if "enrichment" in model_output:
        commands = model_output
        print("Executing command:", commands)
        # 执行命令
        os.system(commands.strip())
        file_content = read_file_with_cat("Forenrich.list.goout")
        drawcontent =convertPointdata_to_echart_format(file_content) 
        os.system("rm Forenrich.list.goout")
        seqres = file_content.replace("\n", "<br>")
        # 使用 <br> 实现换行
        return f"Had been Executed: <br><br> {commands} <br><br> The gene list enrichment is: <br><br> {seqres} <br><br> {drawcontent}"         
    
def convert_to_echart_format(data):
    # 分割数据
    lines = data.strip().split('\n')
    headers = lines[0].split(',')
    gene_data = lines[1].split(',')

    # 提取基因名称
    gene_name = gene_data[0]

    # 提取样本名称和对应的值
    samples = headers[1:]
    values = [float(value) for value in gene_data[1:]]

    # 构建完整的 ECharts 配置
    echart_config = {
        "title": {
            "text": f"Gene Expression - {gene_name}"  # 标题包含基因名称
        },
        "xAxis": {
            "type": "category",
            "data": samples ,
            "axisLabel": { "interval": 0,"rotate": 30} # xAxis 数据为样本名称
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "name": "表达量",
            "type": "bar",
            "data": values  # yAxis 数据为样本对应的值
        }]
    }

    # 返回格式化的 JSON 字符串
    return f"<echart>{json.dumps(echart_config, indent=4)}</echart>"




def read_file_with_cat(file_path):
    """
    使用 cat 命令读取文件内容并返回。
    
    参数:
        file_path (str): 文件的路径。
    
    返回:
        str: 文件的内容。
    """
    try:
        # 使用 subprocess.run 执行 cat 命令，并捕获输出
        result = subprocess.run(["cat", file_path], capture_output=True, text=True, check=True)
        # 返回标准输出内容
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，返回错误信息
        return f"Error: {e.stderr}"

def clean_output(model_output):
    """
    清洗模型输出，提取正式内容，过滤掉 <think> 和 </think> 标签之间的内容。
    
    参数:
        model_output (str): 模型生成的原始输出内容。
    
    返回:
        str: 清洗后的正式输出内容。
    """
    # 使用正则表达式去除 <think> 和 </think> 标签及其内容
    cleaned_output = re.sub(r"<think>.*?</think>", "", model_output, flags=re.DOTALL)
    return cleaned_output.strip()

def execute_blast_command(model_output):
    """
    检测模型输出是否为 blast 命令，如果是则执行命令。
    
    参数:
        model_output (str): 模型生成的输出内容。
    
    返回:
        str: 执行结果或空字符串（如果未执行命令）。
    """
    if "blastn" in model_output:
        # 提取命令部分（假设命令以分号分隔）
        commands = model_output
        print("Executing command:", commands)
        # 执行命令
        os.system(commands.strip())
        file_content = read_file_with_cat("blastn_results.txt")
        os.system("rm blastn_results.txt")
        file_content = "Qseqid\tSseqid\tPident\tLength\tMiss\tGap\tQstart\tQend\tSstart\tSend\tEvalue\tBitscore\n"+ file_content 
        blares =  csv_to_html_from_string(file_content.replace("\t", ","))
        
        # 使用 <br> 实现换行
      #  return f"Had been Executed: <br><br> {commands} <br><br> The Blastn result is: <br><br> {blares}"
        return f"Your requests Had been Executed, The Blastn result is: <br><br> {blares}"
    if "blastp" in model_output:
        # 提取命令部分（假设命令以分号分隔）
        commands = model_output
        print("Executing command:", commands)
        # 执行命令
        os.system(commands.strip())
        file_content = read_file_with_cat("blastp_results.txt")
        os.system("rm blastp_results.txt")
        
        file_content = "Qseqid\tSseqid\tPident\tLength\tMiss\tGap\tQstart\tQend\tSstart\tSend\tEvalue\tBitscore\n"+ file_content 
        blares =  csv_to_html_from_string(file_content.replace("\t", ","))
        # 使用 <br> 实现换行
       # return f"Had been Executed: <br><br> {commands} <br><br> The Blastp result is: <br><br> {blares}"
        return f"Your requests Had been Executed, The Blastp result is: <br> {blares}"


def extractseq_command(model_output):
    if "seqacq" in model_output:
        commands = model_output
        print("Executing command:", commands)
        # 执行命令
        os.system(commands.strip())
        file_content = read_file_with_cat("outseq.fa")
        os.system("rm outseq.fa")
        seqres = file_content.replace("\n", "<br>")
        # 使用 <br> 实现换行
        #return f"Had been Executed: <br><br> {commands} <br><br> The extracted sequence is: <br><br> {seqres}"     
        return f"Your requests Had been Executed, The extracted sequence is: <br> {seqres}"

def getgeneseq_command(model_output):
    if "tempgene" in model_output:
        commands = model_output
        print("Org Executing command:", commands)
        ifonlyonegene = cleangenelist(commands)
        if ifonlyonegene.find("only one")!= -1:            
           # 执行命令    
            commands = ifonlyonegene.split(":")[1] #命令替换为唯一基因号
            print("Mod Executing command:", commands)
            os.system(commands.strip())
            file_content = read_file_with_cat("tempgene.fa")
            os.system("mv tempgene.fa tempgeneprevious.fa")
           # os.system("rm tempgene.fa")
            seqres = file_content.replace("\n", "<br>")
            # 使用 <br> 实现换行
            #return f"Had been Executed: <br><br> {commands} <br><br> The extracted sequence is: <br><br> {seqres}"     
            return f"Your requests Had been Executed, The extracted sequence is: <br><br> {seqres}"
        else:
            return f"Your request gene match multiple or none gene including: <br> {ifonlyonegene} <br> We suggest using the form of independent gene identifiers for input (e.g. Os01g0929500)"
    
def getgeneloc_command(model_output):
    if "tempgtfgene" in model_output:
        commands = model_output
        print("Executing command:", commands)
        ifonlyonegene = cleangenelist(commands)
        print(ifonlyonegene)
        if ifonlyonegene.find("only one")!= -1:
        # 执行命令
            commands = ifonlyonegene.split(":")[1]
            os.system(commands.strip())
            file_content = read_file_with_cat("tempgtfgene.gtf")
            file_content  = "Chromosome\tType\tStart\tEnd\tDirection\tAnnotation\n"+file_content 
            file_content =  txt_to_html_from_string(file_content) 
            seqres = file_content
            os.system("rm tempgtfgene.gtf")
     #       seqres = file_content.replace("\n", "<br>")
            # 使用 <br> 实现换行
            #return f"Had been Executed: <br><br> {commands} <br><br> The extracted sequence is: <br><br> {seqres}"     
            return f"Your requests Had been Executed, The extracted sequence is:<br> {seqres}"
        else:
            return f"Your request gene match multiple or none gene including: <br> {ifonlyonegene} <br>  We suggest using the form of independent gene identifiers for input (e.g. Os01g0929500)"
    
def search_command(model_output):
    if "genome.ann" in model_output:
        commands = model_output
      #  print("Executing command:", commands)
        # 执行命令
        os.system(commands.strip())
        os.system("awk -F '\t' '{print $1,$2,$3,$4}' outgene.ann > outgene.clean.ann")
        file_content = read_file_with_cat("outgene.clean.ann")
        #os.system("rm outgene.ann")
        
        os.system("rm outgene.clean.ann")
        seqres = file_content.replace("\n", "<br>")
        # 使用 <br> 实现换行
        # return f"Had been Executed: <br><br> {commands} <br><br> The associated gene list is: <br><br> {seqres}"  
        return f"Your requests Had been Executed, The associated gene list is: <br> {seqres}"        
    
def getexprssionanddraw_command(model_output):
    if "expnormalized_counts" in model_output:
        commands = model_output
        print("Executing command:", commands)
        ifonlyonegene = cleangenelist(commands)
        if ifonlyonegene.find("only one")!= -1:
            commands = ifonlyonegene.split(":")[1]
        # 执行命令
            os.system(commands.strip())      
            file_content = read_file_with_cat("run.expnormalized_counts.csv")
            if commands.find("draw it") != -1:
                drawcontent = convert_to_echart_format(file_content)
                os.system("rm run.expnormalized_counts.csv")
                seqres = file_content.replace("\n", "<br>")
                return f"Your requests Had been Executed,The extracted gene expression (normalize counts) is: <br> {seqres} <br>{drawcontent}"
            else:
                drawcontent = file_content
                os.system("rm run.expnormalized_counts.csv")
                seqres  = csv_to_html_from_string(file_content)
             #   seqres = file_content.replace("\n", "<br>")
            # 使用 <br> 实现换行
            #return f"Had been Executed: <br> {commands} <br> The gene expressionlist is: <br> {vartableres}" 
                return f"Your requests Had been Executed,The extracted gene expression (normalize counts) is: <br> {seqres}" 
        else:
            return f"Your request gene match multiple or none gene including: <br> {ifonlyonegene} <br>  We suggest using the form of independent gene identifiers for input (e.g. Os01g0929500 for rice; AT3G49470 for Arabidopsis)"
            
    
def variation_command(model_output):
    if "population" in model_output:
        commands = model_output
        print("Executing command:", commands)
        # 执行命令
        os.sy:stem(commands.strip())
        os.system("python buildvarmatrix.py  output_variation.ped output_variation.map")
        file_content = read_file_with_cat("output_genotypes.csv")
        vartableres = csv_to_html_from_string(file_content)
        os.system("mv  output_genotypes.csv  output_genotypes.previous.csv")
        
       # os.system("rm output_genotypes.csv")
       # seqres = file_content.replace("\n", "<br>")

        # 使用 <br> 实现换行
        #return f"Had been Executed: <br><br> {commands} <br><br> The extracted gene list is: <br><br> {vartableres}" 
        return f"Your requests Had been executed, The extracted variation list is: <br> {vartableres}"
        

@app.route("/generate", methods=["POST"])
def chat(): 
    # 从请求中获取用户输入和 Session ID
    user_input = request.json.get("message")
    conversation_histories = defaultdict(list)
    session_id = request.json.get("session_id")  # 假设前端传递 Session ID
    rethinked = request.json.get('rethinked', False)
    if not session_id:
        return jsonify({"error": "No session_id provided"}), 400

        # 获取当前用户的对话历史
    conversation_history = conversation_histories[session_id]
    
    
    if user_input.startswith("@User usage query:"): #说明书模式
        conversation_history.append(f"User:{user_input}")
        prompt2 = pre_prompt2 + "\n".join(conversation_history)  # 将预先激励和对话历史拼接成一个字符串
        prompt2 += "\nAI:"  # 提示模型生成 AI 的回复
        #用户提问
        try:
            print("The user said:",prompt2)
            prompt2 = prompt2 +"\n"+ read_file_with_cat("description.txt") + "\n" # + "<think> \n" #微调后模型需要加<think>
            
            response = requests.post(
                MODEL_API_URL,
                json={
                    "model": "deepseek-r1-14b-8klt",  # 模型名称
                    "prompt": prompt2,  # 包含上下文的提示
                    "stream": False  # 是否流式输出
                }
            )
            response.raise_for_status()  # 检查请求是否成功

            # 获取模型生成的回复
            model_output = response.json().get("response")
            print("Raw Model Output:", model_output)

            # 清洗输出，去除 think 部分
            cleaned_output = clean_output(model_output)
            print("Cleaned Model Output:", cleaned_output)
            return jsonify({"response": cleaned_output})
        except requests.exceptions.RequestException as e:
            # 如果请求失败，返回错误信息
            return jsonify({"error": str(e)}), 500



    else:
        # 如果启动深度思考，使用上一次的 cleaned_output 作为输入
        if rethinked:
            last_cleaned_output = last_cleaned_outputs.get(session_id)
            if not last_cleaned_output:
                return jsonify({"error": "No previous output available for rethinking"}), 400
            user_input = "这是深度思考任务：根据上一次的生成："+last_cleaned_output+"。深度思考，总结输出特征。"
            print("深度思考内容：",user_input)# 使用上一次的 cleaned_output 作为输入
            prompt = pre_prompt + "\n".join(conversation_history) + user_input # + "\n <think> \n"
            
        else:
            # 将用户输入添加到对话历史
            conversation_history.append(f"User:{user_input}")

        # 构造包含上下文的提示
            prompt = pre_prompt + "\n".join(conversation_history)  #      将预先激励和对话历史拼接成一个字符串
            prompt += "\nAI:" # +    "<think>"  # 提示模型生成 AI 的回复

        print(f"Current Conversation History for Session {session_id}:")
        print(prompt)

        # 调用模型 API
        try:
            start = time.perf_counter() 
            response = requests.post(
                MODEL_API_URL,
                json={
                    "model": "deepseek-r1-14b-8klt",  # 模型名称
                    "prompt": prompt,  # 包含上下文的提示
                    "stream": False  # 是否流式输出
                }
            )
            response.raise_for_status()  # 检查请求是否成功
            end = time.perf_counter() 
            
            
            # 获取模型生成的回复
            model_output = response.json().get("response")
            tokenscost = count_think_tokens(model_output)
            #tokenscost = count_think_tokens("<think>"+"\n"+model_output)
            #print(f"### 思考耗时: {end - start:.6f} 秒",f"思考token长度: {tokenscost}")
            print("Raw Model Output:", model_output)
            

            # 清洗输出，去除 think 部分
            cleaned_output = clean_output(model_output)
            #cleaned_output = clean_output("<think> \n"+model_output)
            print("Cleaned Model Output:", cleaned_output)
            print(f"### 思考耗时: {end - start:.6f} 秒",f"思考token长度: {tokenscost}")
            # 将 AI 的回复添加到对话历史
            if not rethinked:  # 如果是深度思考，不重复添加历史
                conversation_history.append(f"AI: {cleaned_output}")

            # 存储上一次的 cleaned_output
            #last_cleaned_outputs[session_id] = cleaned_output
            dthink =""
            # 检测并执行 blastn 命令（仅在正式输出中检测）
            execution_result = execute_blast_command(cleaned_output)
            if execution_result:
                cleaned_output = "Run order with Sequence Blast <br><br>"
              #  cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                print(execution_result)
                dthink =execution_result
                cleaned_output += execution_result

            # 检测并执行 seq 命令（仅在正式输出中检测）
            extractseq_result = extractseq_command(cleaned_output)
            if extractseq_result:
                cleaned_output = "Run order with Sequence extraction <br><br>"
            #    cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                dthink =extractseq_result
                print(extractseq_result)
                cleaned_output += extractseq_result

            # 检测并执行 search 命令（仅在正式输出中检测）
            search_result = search_command(cleaned_output)
            if search_result:
                cleaned_output = "Run order with Function Search <br><br>"
               # cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                dthink =search_result 
                print(search_result)
                cleaned_output += search_result

            # 检测并执行 expression 命令（仅在正式输出中检测）
            getexprssionanddraw_result = getexprssionanddraw_command(cleaned_output)
            if getexprssionanddraw_result:
                cleaned_output = "Run order with Function Search <br><br>"#+ cleaned_output + " <br><br>"
             #   cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                dthink =getexprssionanddraw_result
                print(getexprssionanddraw_result)
                cleaned_output += getexprssionanddraw_result

            # 检测并执行 variation 命令（仅在正式输出中检测）
            variation_result = variation_command(cleaned_output)
            if variation_result:
                cleaned_output = "Run order with Variation Search <br><br>"#+ cleaned_output + " <br><br>"
               # cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                print(variation_result)
                os.system("head -n 10 output_genotypes.previous.csv > output_genotypes.previous.head.csv")
                dthink =  read_file_with_cat("output_genotypes.previous.head.csv")
                cleaned_output += variation_result
            #检测并执行enrichment命令（仅在正式输出中检测）
            enrichment_result =  getenrichment_command(cleaned_output)
            if enrichment_result: 
                cleaned_output = "Run order with Gene enrichment<br><br>"
        #        cleaned_output = "Run order with: <br><br>" + cleaned_output + " <br><br>"
                print(enrichment_result)
                dthink = enrichment_result
                cleaned_output += enrichment_result
             # 检测并执行 getgeneseq 命令（仅在正式输出中检测）
            getgeneseq_result = getgeneseq_command(cleaned_output)
            if getgeneseq_result:   
                cleaned_output = "Run order with Gene Get Sequence<br><br>"
                print(cleaned_output)
                dthink = getgeneseq_result
                cleaned_output += getgeneseq_result
            getgeneloc_result = getgeneloc_command(cleaned_output)    
            if getgeneloc_result:   
                cleaned_output = "Run order with Gene Get Location<br><br>"
                print(cleaned_output)
                dthink = getgeneloc_result
                cleaned_output += getgeneloc_result

            last_cleaned_outputs[session_id] = dthink
            #i 返回 AI 的回复
            
            if rethinked:
                print("##Rethinked:",cleaned_output)
                population_hapresult =  population_hapcommand(cleaned_output)
                Protein_eleresult =  Protein_elecommand(cleaned_output)
                if population_hapresult:
                  #  cleaned_output = "Run order with summarize haplotype. <br><br> \n"
                    cleaned_output = population_hapresult
                    print(cleaned_output)
                
                elif Protein_eleresult:
                    cleaned_output = "Run order with Calculation of protein properties.<br>"
                    cleaned_output += Protein_eleresult               
                else:                    
                    cleaned_output = "Run order with Re-thinked<br><br>" + cleaned_output 
                    cleaned_output = cleaned_output.replace("\n","<br>")
            return jsonify({"response": cleaned_output})
        
        except requests.exceptions.RequestException as e:
            # 如果请求失败，返回错误信息
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
