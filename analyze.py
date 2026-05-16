import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft TaHei']
plt.rcParams['axes.unicode_minus'] = False

with open('history_row.json', 'r', encoding = 'utf-8') as f:
    raw_data = json.load(f)

records = []
for item in raw_data:
    title = item.get('title', '标题')
    author = item.get('author_name', 'UP')

    view_at = item.get('view_at', 0)
    if view_at:
        view_time = datetime.fromtimestamp(view_at)
    else:
        view_time = None

    progress = item.get('progress', 0)
    duration = item.get('duration', 0)

    if duration > 0:
        completion = progress / duration
    else:
        completion = 0

    records.append({
        '标题': title,
        'UP': author,
        '观看时间': view_time,
        '观看进度(秒)': progress,
        '视频时长(秒)': duration,
        '完播率': completion
    })

df = pd.DataFrame(records)
print(f"共解析 {len(df)} 条记录")

print("\n=====最常看的UP主 TOP10=====")
top_authors = df['UP'].value_counts().head(10)
print(top_authors)

df['hour'] = df['观看时间'].dt.hour
hourly = df['hour'].value_counts().sort_index()
print("\n=====观看时段分布=====")
for h, count in hourly.items():
    bar = '█' * (count // 5)
    print(f"{h:2d}点: {bar} ({count}次)")

high_completion = len(df[df['完播率'] > 0.8])
print(f"\n=====完播率统计=====")
print(f"完播率>80的视频: {high_completion} 个 ({high_completion / len(df) * 100:.1f}%)")
print(f"平均完播率: {df['完播率'].mean()*100:.1f}")


fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
top_authors.head(10).plot(kind='barh', ax=ax1, color='steelblue')
ax1.set_title('最常看UP TOP10')
ax1.set_xlabel('观看次数')
ax1.invert_yaxis()

ax2 = axes[0, 1]
hourly.reindex(range(24), fill_value=0).plot(kind='bar', ax=ax2, color='orange')
ax2.set_title('24小时观看时间分布')
ax2.set_xlabel('小时')
ax2.set_ylabel('视频数量')

ax3 = axes[1, 0]
df['完播率区间'] = pd.cut(df['完播率'], bins=[0, 0.2, 0.5, 0.8, 1.0],
                        labels=['0-20%', '20-50%', '50-80%', '80-100%'])
df['完播率区间'].value_counts().sort_index().plot(kind='bar', ax=ax3, color='green')
ax3.set_title('视频完播率分布')
ax3.set_xlabel('完播率区间')
ax3.set_ylabel('视频数量')

ax4 = axes[1, 1]
df['日期'] = df['观看时间'].dt.date
daily = df['日期'].value_counts().sort_index()
ax4.plot(daily.index, daily.values, marker='o', color='red')
ax4.set_title('日度观看趋势')
ax4.set_xlabel('日期')
ax4.set_ylabel('视频数量')

ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax4.xaxis.set_major_locator(mdates.DayLocator(interval = 1))
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('bilibili_analysis.png', dpi = 150)
plt.show()
print("\n分析图表已保存为 bilibili_analysis.png")