# DeepPGDB
Guided by these transformative advancements in large language model, we introduce DeepPGDB, the first AI-driven plant genomics database (https://deeppgdb.chat/). By combining model fine-tuning and prompt engineering, DeepPGDB represents a novel paradigm for interactive genomic databases. It is specifically designed to lower technical barriers, enabling seamless analysis of complex omics data based on high-quality genomes.

DeepPGDB allows users from diverse academic backgrounds to intuitively access, analyze, and visualize genomic data through natural language queries. This innovative approach addresses a critical need in the field, empowering researchers to conduct more productive and inclusive plant genomics research. By leveraging the power of AI, DeepPGDB sets a new standard for the way we interact with and utilize genomic databases, paving the way for breakthroughs in plant genomics.

**Usage**
The user needs to prepare a local model interface. Furthermore, modify the flask API call path in the main file to the path of their own model resources. The model can use API interfaces such as ollama vllm for support.

The model file can be downloaded [here](https://www.modelscope.cn/models/LEECHXP/DeepPGDB).

Run the order with
```
python main.py source.cfg
```



