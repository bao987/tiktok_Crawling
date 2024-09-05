import datetime
from DrissionPage import ChromiumPage
import csv
import sqlite3

# 连接到数据库SQLite
conn = sqlite3.connect('douyin.db') #连接到数据库文件douyin.db，不存在会在当前目录创建
c = conn.cursor()#创建一个cursor对象并使用它执行SQL命令
c.execute('''  
CREATE TABLE IF NOT EXISTS messages (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    nickname TEXT NOT NULL,  
    ip_label TEXT NOT NULL,  
    date TEXT NOT NULL,  
    text TEXT NOT NULL  
)  
''')

# 创建CSV文件并写入表头
with open('data.csv', mode='w', encoding='utf-8-sig', newline='') as f:
    csv_writer = csv.DictWriter(f, fieldnames=['昵称', '地区', '时间', '评论'])
    csv_writer.writeheader()

# 初始化数据收集列表
data_list = []

# 打开浏览器并监听数据包
driver = ChromiumPage()
driver.listen.start('aweme/v1/web/comment/list/')
driver.get('https://www.douyin.com/video/7394306433350749475')

# 爬取评论数据
for page in range(100):
    print(f'正在采集第{page + 1}页的数据内容')
    driver.scroll.to_bottom() # 下滑页面到底部
    resp = driver.listen.wait() # 等待数据包加载
    json_data = resp.response.body
    comments = json_data.get('comments', [])  # 确保comments是一个列表

    # 提取comments中需要的部分
    for index in comments:
        # 键值对取值，提取相关内容
        text = index['text'] #评论内容
        nickname = index['user']['nickname'] #评论者昵称
        create_time = index['create_time'] #评论日期
        date = datetime.datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')  # 格式化日期
        ip_label = index['ip_label'] #评论ip地址

        # 将数据添加到列表中
        data_list.append({
            '昵称': nickname,
            '地区': ip_label,
            '时间': date,
            '评论': text
        })

        # 同时写入CSV
        with open('data.csv', mode='a', encoding='utf-8-sig', newline='') as f:
            csv_writer = csv.DictWriter(f, fieldnames=['昵称', '地区', '时间', '评论'])
            csv_writer.writerow({
                '昵称': nickname,
                '地区': ip_label,
                '时间': date,
                '评论': text
            })

# 遍历数据列表并插入到数据库中
for item in data_list:
    c.execute("INSERT INTO messages (nickname, ip_label, date, text) VALUES (?, ?, ?, ?)",
              (item['昵称'], item['地区'], item['时间'], item['评论']))

# 提交事务
conn.commit()

# 关闭连接
conn.close()

print("该抖音评论数据已成功写入数据库！")