import sqlite3

# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建:
conn = sqlite3.connect('douyin.db')

# 创建一个Cursor:
c = conn.cursor()

# 执行查询
c.execute('SELECT * FROM messages')

# 获取所有查询结果
rows = c.fetchall()

# 打印结果
for row in rows:
    print(row)

# 关闭Connection:
conn.close()