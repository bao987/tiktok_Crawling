# 对于文件1已经爬取到且保存在数据库中的数据进行处理，预处理过程在文件2中，其余数据分析在文件3
# 1.数据预处理 包括去除HTML标签，去除符号表情等，去除停用词，将预处理后的数据保存在新表cleaned_messages中(SQLite数据库在表建立后不可以新增列）
# 2.绘制词云图 对评论内容绘制词云图
# 3.评论时间趋势
# 4.主题建模
# 5.情感分类
# 6.ip地址划分

import sqlite3
import re
import jieba

# 连接到SQLite数据库
conn = sqlite3.connect('douyin.db')
cursor = conn.cursor()

# 读取原始messages表的id和text
cursor.execute("SELECT id, text FROM messages")
comments = cursor.fetchall()


# 清洗函数
def clean_text(text):
    text = re.sub('<[^<]+?>', '', text)  # 去除HTML标签
    text = re.sub(r'[^\u4e00-\u9fa5\w]', '', text)  # 保留中文字符、英文字母和数字，去除其他符号
    stopwords = set(['的', '了', '在', '是', '和', '与', '但', '不过', '然而', '如果', '虽然', '因为', '所以',
                     '有', '没有', '这个', '那个', '这些', '那些', '一个', '一种', '之', '对于', '关于', '对于',
                     '对于', '由于', '通过', '随着', '对', '被', '让', '把', '比', '按照', '以及', '则', '它',
                     '它们', '其实', '已经', '自己', '自己', '我们', '你们', '他们', '大家', '或者', '还是', '也',
                     '又', '就', '才', '却', '只', '但', '不', '没有', '很', '非常', '十分', '特别', '极其', '太',
                     '更', '还', '最', '挺', '相当', '稍微', '略微', '更加', '越发', '有点儿', '了', '着', '过', '呢',
                     '啊', '呀', '吗', '吧', '啦'])  # 停用词列表
    words = jieba.cut(text)
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    return ' '.join(filtered_words)


# 应用清洗函数
cleaned_comments = [(id, clean_text(text)) for id, text in comments]

# 创建一个新表来存储清洗后的数据
cursor.execute('''  
CREATE TABLE IF NOT EXISTS cleaned_messages (  
    id INTEGER PRIMARY KEY,  
    text TEXT  
)  
''')

# 插入清洗后的数据
cursor.executemany("INSERT INTO cleaned_messages (id, text) VALUES (?, ?)", cleaned_comments)
# 提交事务
conn.commit()

# 查询清洗后的数据表
cursor.execute('SELECT * FROM cleaned_messages')
# 获取所有查询结果
rows = cursor.fetchall()
# 打印结果
for row in rows:
    print(row)



#关闭连接
conn.close()