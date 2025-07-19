import requests


prompt = "根据以下文件内容回答用户提问（如果用户提问时英语请用英语回答）,如果文件里没有记载则回答本数据库中暂无记载,文件内容如下"
file = open("genomeinfo.txt","r")
filecontent = file.read().strip()
file.close()

userfile = open("querygenomeinfo.list","r")
userfilecontent = userfile.read().strip()
userfile.close()

prompt3 = prompt + filecontent + "用户提问:" + userfilecontent
response = requests.post(
                "http://DeepPGDB.ipyingshe.net:10930/api/generate",
                json={
                    "model": "gemma3:12b",  # 模型名称
                    "prompt": prompt3,  # 包含上下文的提示
                    "stream": False  # 是否流式输出
                }
            )
response.raise_for_status()  # 检查请求是否成功
model_output = response.json().get("response")
print(model_output)
