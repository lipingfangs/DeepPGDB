import math
import json

# 示例数据
data = """GO:0003674 295 392 7303 2638 1.0243885655042517 0.224286235661403 0.5394597040744856
GO:0003676 63 392 1524 8417 1.048333802024747 0.3604372240012625 0.636071026828426
GO:0003723 40 392 838 9103 1.2104865812673518 0.11724670865961646 0.42846860761408995
GO:0003824 194 392 4236 5705 1.1614212965639512 0.003017267807442807 0.3127214279663867
GO:0004518 25 392 427 9514 1.4847595947043923 0.030990733659857966 0.32113627750946533
GO:0004519 21 392 375 9566 1.4201428571428572 0.06653533371017878 0.3884582125556021
GO:0005488 131 392 3408 6533 0.974800439542014 0.6618698700965124 0.8209666754577416
GO:0005575 348 392 8573 1368 1.0294148453735863 0.07616027978950685 0.3884582125556021
GO:0005622 319 392 7384 2557 1.0955772409180358 0.00045140034694400534 0.2663367525765607
GO:0005623 343 392 8333 1608 1.0438467538701548 0.023169344697745724 0.32113627750946533"""

# 解析数据
echarts_data = []
x_data = []  # X 轴数据（倒数第三列）
y_data = []  # Y 轴数据（-log10(倒数第二列)）
size_data = []  # 点的大小（第二列）
color_data = []  # 点的颜色（-log10(倒数第二列)）

for line in data.split('\n'):
    columns = line.strip().split()
    y_value = float(columns[-2])  # 倒数第二列的值

    # 筛选倒数第二列小于0.01的行
    if y_value < 0.01:
        x_data.append(float(columns[-3]))  # X 轴数据
        log_y_value = -math.log10(y_value)  # 计算 -log10(y_value)
        y_data.append(log_y_value)  # Y 轴数据
        size_data.append(float(columns[1]))  # 点的大小
        color_data.append(log_y_value)  # 点的颜色

# ECharts 配置
echarts_config = {
    "title": {
        "text": "GO Terms 散点图"  # 标题
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
        "name": "GO Terms",
        "type": "scatter",
        "data": [[x, y, size, color] for x, y, size, color in zip(x_data, y_data, size_data, color_data)],  # 数据格式: [X, Y, size, color]
        "symbolSize": "function (data) { return data[2]; }",  # 点的大小
        "itemStyle": {
            "color": "function (params) { const colorValue = Math.floor(params.value[3] * 100); return 'rgb(0, 0, ' + colorValue + ')'; }"
        }
    }]
}

# 打印配置
print(json.dumps(echarts_config, indent=4))
