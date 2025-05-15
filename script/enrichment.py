import sys
import pickle  # 用于序列化和反序列化字典
from pathlib import Path  # 用于路径操作
from scipy import stats
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector

statsr = importr('stats')

def goread(goingo, cache_dir="cache"):
    # 缓存文件路径
    cache_file = Path(cache_dir) / f"{Path(goingo).stem}_cache.pkl"
    
    # 如果缓存文件存在，则直接加载
    if cache_file.exists():
        with open(cache_file, "rb") as f:
            print(f"Loading cached data from {cache_file}")
            return pickle.load(f)
    
    # 如果缓存文件不存在，则解析原始文件并保存缓存
    dicgonum = {}
    dicgenegolist = {}
    totalgenenum = 0

    with open(goingo, "r") as filego:
        for line in filego:
            totalgenenum += 1
            parts = line.strip().split()
            gene = parts[0]
            dicgenegolist[gene] = []
            if len(parts) > 1:
                for go_term in parts[1].split(","):
                    if "GO" in go_term:  # only for Go
                        go_term = go_term.strip()
                        dicgenegolist[gene].append(go_term)
                        dicgonum[go_term] = dicgonum.get(go_term, 0) + 1

    # 将结果保存到缓存文件
    Path(cache_dir).mkdir(parents=True, exist_ok=True)  # 确保缓存目录存在
    with open(cache_file, "wb") as f:
        print(f"Saving cached data to {cache_file}")
        pickle.dump((dicgonum, dicgenegolist, totalgenenum), f)

    return dicgonum, dicgenegolist, totalgenenum

def enrichment(m, n, a, b):  # enrichment test adjustment
    return stats.hypergeom.sf(m, n, a, b)

def main():
    goin = sys.argv[1]
    goingo = sys.argv[2]
    goout = sys.argv[3]

    # 读取 GO 数据（如果缓存存在则直接加载）
    dicgonum, dicgenegolist, totalgenenum = goread(goingo)

    with open(goin, "r") as file2, open(goout, "w") as gogoout:
        liness = file2.readlines()[0].split(",")
        dicquerygonum = {}
        dicquerylist = set()
        samplenum = 0
        mapnum = 0

        for line in liness:
            gene = line.strip()
            samplenum += 1
            if gene in dicgenegolist:
                for go_term in dicgenegolist[gene]:
                    dicquerygonum[go_term] = dicquerygonum.get(go_term, 0) + 1
                    dicquerylist.add(go_term)
                mapnum += 1

        if mapnum == 0:
            print("No gene mapped, check your data!")
            return

        print(f"{mapnum} genes mapped")

        pvaluelist = []
        for go_term in dicquerygonum:
            m = dicquerygonum[go_term] - 1
            n = totalgenenum
            a = dicgonum[go_term]
            b = mapnum
            pvalue = enrichment(m, n, a, b)
            pvaluelist.append(pvalue)

        p_adjust = statsr.p_adjust(FloatVector(pvaluelist), method='BH')

        for go_term, pvalue, padj in zip(dicquerygonum.keys(), pvaluelist, p_adjust):
            oa = dicquerygonum[go_term]
            ob = mapnum
            oc = dicgonum[go_term]
            od = totalgenenum - dicgonum[go_term]
            fc = (oa/ob)/(oc/totalgenenum)
            print(go_term, oa, ob, oc, od,fc, pvalue, padj, file=gogoout)

if __name__ == "__main__":
    main()

