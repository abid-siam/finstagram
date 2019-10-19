import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
