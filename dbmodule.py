# DB
import sqlite3
import os

# アプリ定数
DBMANE = 'database/database.db'

# ---------------------------------------------------------------------------
# dbmodule
#
# データベース操作用の関数を分離
# ---------------------------------------------------------------------------
# データベース生成
# ---------------------------------------------------------------------------
def create_database():
    # ディレクトリ確認
    try:
        os.makedirs('database')
    except:
        pass
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        # categoryテーブルの定義
        ddl = """
        CREATE TABLE category
        (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
        """
        c.execute(ddl)
        # デフォルト：なし
        c.execute("INSERT INTO category VALUES(1,'なし')")
        # itemテーブルの定義
        ddl = """
        CREATE TABLE items
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            maintext TEXT,
            FOREIGN KEY(category_id) REFERENCES category(category_id)
            ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
        c.execute(ddl)
    except:
        print('作成エラー')
    c.commit()
    c.close()

# ---------------------------------------------------------------------------
# メモ全件取得
# ---------------------------------------------------------------------------
def select_memo():
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT id, name, category_name, maintext
        FROM items as i, category as c
        WHERE i.category_id = c.category_id
        """
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# メモ1件取得
# ---------------------------------------------------------------------------
def select_memo_one(id):
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT id, name, category_name, maintext
        FROM items as i, category as c
        WHERE i.category_id = c.category_id
        AND id = {}
        """.format(id)
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# カテゴリ別メモ取得
# ---------------------------------------------------------------------------
def select_memo_category(category):
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT id, name, category_name, maintext
        FROM items as i, category as c
        WHERE i.category_id = c.category_id
        AND i.category_name = '{}'
        """.format(category)
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# メモ登録
# ---------------------------------------------------------------------------
def insert_memo(memo):
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        print(memo)
        sql = """
        INSERT INTO items(name, category_id, maintext)
        VALUES('{}', {}, '{}')
        """.format(memo[0], memo[1], memo[2])
        c.execute(sql)
        c.commit()
        c.close()
        print('登録成功')
    except:
        print('登録エラー')

# ---------------------------------------------------------------------------
# メモ編集
# ---------------------------------------------------------------------------
def update_memo(memo):
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        print(memo)
        sql = """
        UPDATE items
        SET name = '{}', category_id = {}, maintext = '{}'
        WHERE id = {}
        """.format(memo[0], memo[1], memo[2], memo[3])
        c.execute(sql)
        c.commit()
        c.close()
        print('更新成功')
    except:
        print('更新エラー')

# ---------------------------------------------------------------------------
# メモ削除
# ---------------------------------------------------------------------------
def delete_memo(id):
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        DELETE FROM items
        WHERE id = {}
        """.format(id)
        c.execute(sql)
        c.commit()
        c.close()
        print('削除成功')
    except:
        print('削除エラー')

# ---------------------------------------------------------------------------
# カテゴリ全件取得
# ---------------------------------------------------------------------------
def select_category():
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT category_id, category_name
        FROM category
        """
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# カテゴリ名取得
# ---------------------------------------------------------------------------
def select_category_name(c_id):
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT category_name
        FROM category as c
        WHERE c.category_id = {}
        """.format(c_id)
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# カテゴリID取得
# ---------------------------------------------------------------------------
def select_category_id(c_name):
    result = []
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        SELECT category_id
        FROM category as c
        WHERE c.category_name = '{}'
        """.format(c_name)
        result = c.execute(sql)
        print('取得完了')
    except:
        print('取得エラー')
    return list(result)

# ---------------------------------------------------------------------------
# カテゴリ登録
# ---------------------------------------------------------------------------
def insert_category(c_name):    
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        print(c_name)
        sql = """
        INSERT INTO category(category_name)
        VALUES('{}')
        """.format(c_name)
        c.execute(sql)
        c.commit()
        c.close()
        print('登録成功')
    except:
        print('登録エラー')

# ---------------------------------------------------------------------------
# カテゴリ削除
# ---------------------------------------------------------------------------
def delete_category(c_id):
    c = sqlite3.connect(DBMANE)
    c.execute("PRAGMA foreign_keys = ON")
    try:
        sql = """
        DELETE FROM category
        WHERE category_id = {}
        """.format(c_id)
        c.execute(sql)
        c.commit()
        c.close()
        print('削除成功')
    except:
        print('削除エラー')
