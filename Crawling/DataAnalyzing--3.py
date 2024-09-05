'''
此前对于爬取的评论，原始评论存储在表messages中，清洗后的数据存储在cleaned_messages中
对评论将作如下处理
1.绘制词云图  对于cleaned_messages中的数据绘制词云图并展示
   词云图
2.评论时间趋势图 对于messages表中的评论时间绘制条形图，观察随着时间变化评论数的趋势改变情况
   随时间变化的评论柱形图
3.ip地址划分
   随地点改变的地图
4.主题建模 对于每条评论提取主题形成摘要
5.情感分类 对于每条评论进行情感分析，情感得分决定正向负向
   45得到每条评论的情感分数和主题
'''
import jieba
from wordcloud import WordCloud
from pyecharts.charts import Map
from pyecharts import options as opts
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from snownlp import SnowNLP
from gensim import corpora, models


#1.绘制词云图
# 一个支持中文的字体文件路径
font_path = 'C:\Windows\Fonts\STXINGKA.TTF'  # 字体文件路径

# 连接到SQLite数据库
conn = sqlite3.connect('douyin.db')
c = conn.cursor()

# 执行SQL查询以获取所有已清洗的文本数据
c.execute('SELECT text FROM cleaned_messages')
cleaned_texts = [row[0] for row in c.fetchall()]

# 将所有文本合并成一个长字符串
text = ' '.join(cleaned_texts)

# 创建词云对象
wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate(text)

# 显示词云图
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 不显示坐标轴
plt.show()

#**************************************************************************************************************************************
#2.评论时间趋势图
# 连接到SQLite数据库
df = pd.read_sql_query('SELECT date FROM messages', conn)

# 确保date列是日期时间类型
df['date'] = pd.to_datetime(df['date'])

# 将日期转换为年份和周数（ISO周）
df['year'] = df['date'].dt.year
df['week'] = df['date'].dt.isocalendar().week

# 按年份和周数分组，并计算每个组的记录数
weekly_counts = df.groupby(['year', 'week']).size().reset_index(name='count')

# 为了绘图方便，将年份和周数合并为一个日期列（这里取每周的第一天作为代表）
weekly_counts['week_start'] = pd.to_datetime(weekly_counts.apply(lambda x: f'{x["year"]}-{x["week"]}-1', axis=1),
                                             format='%Y-%W-%w')

# %W-%w格式可能不是所有pandas版本都支持，可以使用dateutil的relativedelta来更准确地获取每周的第一天
# 需要先安装dateutil: pip install python-dateutil
# from dateutil.relativedelta import relativedelta
# weekly_counts['week_start'] = weekly_counts.apply(lambda x: x['date'].iloc[0] - pd.to_timedelta(x['date'].iloc[0].weekday(), unit='d'), axis=1)

# 绘图
plt.figure(figsize=(10, 5))
plt.plot(weekly_counts['week_start'], weekly_counts['count'], marker='o', linestyle='-', color='b')
plt.gcf().autofmt_xdate()  # 自动旋转日期标签以避免重叠
plt.xlabel('Date')
plt.ylabel('Number of Messages')
plt.title('Weekly Message Counts')
plt.grid(True)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置x轴日期格式（这里可能不完全准确，用的是周的开始）
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))  # 每周一作为主刻度
plt.tight_layout()
plt.show()


#**************************************************************************************************************************************************
#3.地图评论数标记
# 省份简称到全称的映射字典
province_mapping = {
    '北京': '北京市',
    '天津': '天津市',
    '上海': '上海市',
    '重庆': '重庆市',
    '河北': '河北省',
    '山西': '山西省',
    '辽宁': '辽宁省',
    '吉林': '吉林省',
    '黑龙江': '黑龙江省',
    '江苏': '江苏省',
    '浙江': '浙江省',
    '安徽': '安徽省',
    '福建': '福建省',
    '江西': '江西省',
    '山东': '山东省',
    '河南': '河南省',
    '湖北': '湖北省',
    '湖南': '湖南省',
    '广东': '广东省',
    '广西': '广西壮族自治区',
    '海南': '海南省',
    '四川': '四川省',
    '贵州': '贵州省',
    '云南': '云南省',
    '西藏': '西藏自治区',
    '陕西': '陕西省',
    '甘肃': '甘肃省',
    '青海': '青海省',
    '宁夏': '宁夏回族自治区',
    '新疆': '新疆维吾尔自治区',
    '内蒙古': '内蒙古自治区',
    '香港': '香港特别行政区',
    '澳门': '澳门特别行政区',
    # 台湾省由于政治原因，部分地图数据源中不被直接列出
}

# 连接到SQLite数据库并读取数据
df = pd.read_sql_query('SELECT ip_label, COUNT(*) as count FROM messages GROUP BY ip_label', conn)

# 使用replace方法或apply方法与自定义函数来更新省份名称
# 使用apply方法更灵活，可以处理更复杂的映射逻辑
df['ip_label'] = df['ip_label'].apply(lambda x: province_mapping.get(x, x))
# 如果x在province_mapping中，则返回对应的全称；否则，返回x本身（即未修改的简称）

# 设置自定义的颜色分段
visual_map_pieces = [
    {"min": 0, "max": 10, "label": "0-10", "color": "#FFFFFF"},  # 白色代表较少的消息数量
    {"min": 11, "max": 50, "label": "11-50", "color": "#FFFF00"},  # 黄色代表中等数量的消息
    {"min": 51, "max": 100, "label": "51-100", "color": "#FF7F00"},  # 橙色代表较多的消息
    {"min": 101, "label": "101+", "color": "#FF0000"}  # 红色代表最多的消息
]

# 根据实际的消息数量范围来调整它们

# 创建地图对象并绘制地图
m = Map()
m.add("评论数量", [list(z) for z in zip(df['ip_label'], df['count'])], "china")
m.set_global_opts(
    title_opts=opts.TitleOpts(title="各省评论数量"),
    visualmap_opts=opts.VisualMapOpts(
        pieces=visual_map_pieces,  # 使用自定义的颜色分段
        is_piecewise=True  # 启用分段式视觉映射
    )
)

# 渲染地图到HTML文件
m.render("province_message_count.html")


#************************************************************************************************************************************************************************
#4.情感分析与主题建模
# 读取数据
df = pd.read_sql_query('SELECT text FROM cleaned_messages', conn)

conn.close()

# 查看前几行数据
print(df.head())

# 首先，清理 'text' 列中的空值或空字符串
df['text'] = df['text'].fillna('')  # 将 NaN 替换为空字符串（如果需要的话）
df = df[df['text'] != '']  # 过滤掉空字符串的行

# 现在应用 SnowNLP 进行情感分析
df['sentiment'] = df['text'].apply(lambda x: SnowNLP(x).sentiments)

# 查看结果
print(df[['text', 'sentiment']])

# 情感分析
df['sentiment'] = df['text'].apply(lambda x: SnowNLP(x).sentiments)

# sentiment 值通常在 [0, 1] 之间，0 为负面，1 为正面
print(df[['text', 'sentiment']].head())

# 准备文档以进行LDA建模
processed_docs = df['text']

# 分词处理
tokenized_docs = [[word for word in jieba.cut(doc, cut_all=False)] for doc in processed_docs]

# 创建字典
dictionary = corpora.Dictionary(tokenized_docs)

# 创建语料库
corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]

# 构建LDA模型
lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)

# 输出主题
topics = lda_model.print_topics(num_words=4)
for topic in topics:
    print(topic)