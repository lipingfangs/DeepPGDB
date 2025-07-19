import pandas as pd
import json
import sys

# 用户可控制的参数
table1 = sys.argv[1]
table2 = sys.argv[2]
sys_max_haplotypes = 3  # 默认展示个体数量最多的前3个单倍型

# 读取表1和表2
table1 = pd.read_csv(table1, sep=',', header=None)
table2 = pd.read_csv(table2, sep='\t', header=None)

# 为表格设置列名
table1.columns = ['ID'] + [f'Pos_{i}' for i in range(1, len(table1.columns))]
table2.columns = ['ID', 'Subspecies']

# 根据表1的单倍型信息生成单倍型标识
haplotypes = table1.drop('ID', axis=1).apply(lambda row: '-'.join(row), axis=1)
table1['Haplotype'] = haplotypes

# 合并表1和表2
merged = pd.merge(table1[['ID', 'Haplotype']], table2, on='ID')

# 按单倍型统计个体数量
haplotype_counts = merged.groupby('Haplotype').size().reset_index(name='TotalCount')
haplotype_distribution = merged.groupby(['Haplotype', 'Subspecies']).size().reset_index(name='Count')

# 按个体总数从大到小排序，并选择前N个单倍型
top_haplotypes = haplotype_counts.sort_values(by='TotalCount', ascending=False).head(sys_max_haplotypes)['Haplotype']

# 过滤单倍型分布数据，只保留前N个单倍型
filtered_distribution = haplotype_distribution[haplotype_distribution['Haplotype'].isin(top_haplotypes)]

# 生成ECharts配置
options = {
    "title": [],
    "dataset": [],
    "series": []
}

dataset_index = 0
x_offset = 22  # 起始横向偏移，整体向右偏移 7%
y_center = 50  # 饼图的垂直中心位置
title_y_offset = 30  # 标题与饼图的垂直间距

for haplotype, group in filtered_distribution.groupby('Haplotype'):
    # 构造 dataset
    dataset = {
        "source": [["Subspecies", "Count"]] + group[['Subspecies', 'Count']].values.tolist()
    }
    options["dataset"].append(dataset)

    # 设置饼图位置和半径
    center_position = [f'{x_offset}%', f'{y_center}%']
    series = {
        "type": "pie",
        "radius": 60,  # 饼图半径
        "center": center_position,
        "datasetIndex": dataset_index,
        "label": {
            "show": True,
            "formatter": "{b}: {d}%",
            "fontSize": 10  # 显示亚种比例
        }
    }
    options["series"].append(series)

    # 为每个饼图添加标题，位置在饼图正上方且不重叠
    title = {
        "text": f"{haplotype} (Total: {group['Count'].sum()})",
        "left": f"{x_offset-10}%",  # 与饼图横向位置对齐
        "top": f"{y_center - title_y_offset-10}%",  # 标题位置稍高于饼图
        "textStyle": {
            "fontSize":6   # 调整标题字号，使标题更小
        }
    }
    options["title"].append(title)

    # 更新横向偏移
    x_offset += 31  # 每个饼图之间横向间隔

    # 更新 dataset 索引
    dataset_index += 1

# 导出 ECharts 配置
with open('haplotype_pie_chart.json', 'w') as f:
    json.dump(options, f, indent=4)

print(f"ECharts配置已生成并保存为 haplotype_pie_chart_right_adjusted.json，展示前{sys_max_haplotypes}个单倍型。")

