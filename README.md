# DeepPGDB
![logo forgithub](https://github.com/user-attachments/assets/69538d08-a602-4bb4-a693-c7299e1e3212)

Guided by these transformative advancements in large language model, we introduce DeepPGDB, the first AI-driven plant genomics database (https://www.deeppgdb.chat/). By combining model fine-tuning and prompt engineering, DeepPGDB represents a novel paradigm for interactive genomic databases. It is specifically designed to lower technical barriers, enabling seamless analysis of complex omics data based on high-quality genomes.

DeepPGDB allows users from diverse academic backgrounds to intuitively access, analyze, and visualize genomic data through natural language queries. This innovative approach addresses a critical need in the field, empowering researchers to conduct more productive and inclusive plant genomics research. By leveraging the power of AI, DeepPGDB sets a new standard for the way we interact with and utilize genomic databases, paving the way for breakthroughs in plant genomics.

**Usage**

The user needs to prepare a local model interface. Furthermore, modify the flask API call path in the main file to the path of their own model resources. The model can use API interfaces such as ollama vllm for support.

The model file can be downloaded [here](https://www.modelscope.cn/models/LEECHXP/DeepPGDB).

Run backend api with the order:
```
python main.py source.cfg
```
The example contain of source.cfg file including:
```
ModelAPI=http://127.0.0.1/generate #Replace as your model API URL
Prompt=./Prompt.txt  #Replace as your own prompt
QueryModel=deepseek-r1-14b-16klt  #Replace as your model name
Tooldir=./script #Replace as your tools dir
Datadir./data #Replace as your tools dir
```

If you want to add the new genome to the model:
```
python Addgenome.py Addgenome.info
```

The example contain of Addgenome.info file including:
```
SpeicesName=Brachypodium.distachyon #<Latin binomial; separated by ".">
CommonName=二穗短柄草 #<common name>
Genome=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.dna.toplevel.fa #<Genome file with fasta format>
cds=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.cds.all.fa #<cds file with fasta format>
cdna=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.cdna.all.fa  #<cdna file with fasta format>
pep=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.pep.all.fa #<pep file with fasta format>
gff=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.61.gff3 #<Annotation file>
functioninfo=Brachypodium_distachyon.Brachypodium_distachyon_v3.0.61.gff3.ann  #<Functional annotation file>
inputinfofile=promptnew3.txt #<Prompt file>
outinfofile=promptnew3.new.txt #<The new Prompt generated with Addvalue.py which utilized in source.cfg file>
#Expression=
#Poputlation=
```

Run the web
replace the 4 lines for backup of index.html

```
const response = await fetch('https://xxxxpgdb.chat/generate', {  #Replace the URL as your flask api start by main.py in last step.
```

