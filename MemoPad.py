# -*- coding: utf-8 -*-
# tkinter
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
# 正規表現
import re
# DB
import sqlite3
# コンフィグ用
import configparser as cp
import os
import sys
# モジュール
import subwindow as sw
import dbmodule as db

# アプリ定数
TITLE = 'ちょっとすごいメモ'
CONFIGNAME = 'config/config.ini'
ROOT_WIDTH = 900
ROOT_HEIGHT = 480
MENU_WIDTH = 180
MAIN_WIDTH = ROOT_WIDTH - MENU_WIDTH

MENU_ITEM = ['一覧表示', '新規作成', 'カテゴリ編集', 'アプリ設定']
CHAR_SET = ['utf-8', 'Unicode', 'Shift-JIS']
CHAR_FONT = ['メイリオ', 'ＭＳ ゴシック', '游ゴシック']
F_SIZE = {'L':20, 'M':15, 'S':10}   # 文字サイズ

# ---------------------------------------------------------------------------
# memopad
#
# いろいろできるメモ帳を練習として制作．
# データベースにメモを保存し，自由に編集可能．
# カテゴリ別に保存することもでき，用途にあわせて見つけやすく．
# ファイル出力も可能．さらに文字コードを指定可能．
# ---------------------------------------------------------------------------
# メインフレーム(アプリ本体)
# ---------------------------------------------------------------------------
class MemoPad(tk.Frame):
    # コンストラクタ
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill=tk.BOTH)
        self.font = CHAR_FONT[0]    # 使用フォント
        self.charset = CHAR_SET[0]  # 使用文字コード(ただし，iniファイルは常時UTF-8)
        self.edit_flag = False  # 編集状態時の移動制限
        self.config_read()      # コンフィグ読み込みor初期生成
        db.create_database()  # (ない場合)DB初期生成
        self.menu_create()
        self.home()
        
    # ---------------------------------------------------------------------------
    # コンフィグ
    #
    # アプリ設定を変更可能．
    # 現状，アプリ本体のフォントおよび出力時の文字コードを指定可能．
    # ---------------------------------------------------------------------------
    # コンフィグ読み込み
    # ---------------------------------------------------------------------------
    def config_read(self):
        try:
            config = cp.ConfigParser()
            config.read(CONFIGNAME, 'utf-8')
            # configの文字列チェック(いろいろいじられてしまったときのため)
            if 'user' in config:
                for i in CHAR_SET:
                    if i == config.get('user', 'charset'):
                        self.charset = i
                        break
                for i in CHAR_FONT:
                    if i == config.get('user', 'font'):
                        self.font = i
                        break
            else:
                self.config_write(self.charset, self.font)
        except:
            pass
   
    # ---------------------------------------------------------------------------
    # ファイル出力
    #
    # データをファイルとして出力．
    # デフォルトではtxtファイル．
    # ---------------------------------------------------------------------------
    def output_file(self, title, text):
        def submit_output(event):
            # ok
            def submit_ok(event):
                sub_sub_win.destroy()
            file = open('files/'+output_title.get(), 'w', encoding=self.charset)
            file.write(text)
            file.close()
            sub_win.destroy()
            sub_sub_win = sw.SubWindow('出力完了', 'ファイルを出力しました！', self.font)
            ok_button = tk.Button(sub_sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
            ok_button.bind('<1>', submit_ok)
            ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        # ファイル用フォルダ生成
        try:
            os.makedirs('files')
        except:
            pass
        # サブウィンドウ
        sub_win = sw.SubWindow('出力内容の確認', '以下のファイルを出力します', self.font)
        output_title = tk.Entry(sub_win.frame, font=(self.font, F_SIZE['S']))
        output_title.pack(fill=tk.X, padx=5, pady=5)
        output_title.insert(tk.END, title+'.txt')
        output_button = tk.Button(sub_win.frame, text='出力', width=8, font=(self.font, F_SIZE['S']))
        output_button.bind('<1>', submit_output)
        output_button.pack(padx=5, pady=5)
        

    # ---------------------------------------------------------------------------
    # コンフィグ書き込み
    # ---------------------------------------------------------------------------
    def config_write(self, charset, font):
        # ディレクトリ確認
        try:
            os.makedirs('config')
        except:
            pass
        config = cp.ConfigParser()
        user = {'charset':charset, 'font':font}
        config['user'] = user
        with open(CONFIGNAME, 'w', encoding='utf-8') as file:
            config.write(file)
        file.close()
        self.charset = charset
        self.font = font
   
    # ---------------------------------------------------------------------------
    # フレーム生成
    #
    # アプリ本体で動作する大枠を生成．
    # ---------------------------------------------------------------------------
    # メニューバー生成
    # ---------------------------------------------------------------------------
    def menu_create(self):
        
        # 画面遷移
        def move(mv):
            # 一覧表示
            if mv.widget['text'] == MENU_ITEM[0]:
                self.home()
            # カテゴリ別表示
            elif mv.widget['text'] == MENU_ITEM[1]:
                self.insert_memo()
            # カテゴリ編集
            elif mv.widget['text'] == MENU_ITEM[2]:
                self.category_edit()
            # アプリ設定
            elif mv.widget['text'] == MENU_ITEM[3]:
                self.app_config()

        # メニューボタン
        def button_action(event):
            # はい(機能移動)
            def submit_yes(event):
                sub_win.destroy()
                move(mv)
            # いいえ(中断)
            def submit_no(event):
                sub_win.destroy()
                return
            
            mv = event
            if self.edit_flag == True:
                # サブウィンドウ
                sub_win = sw.SubWindow('移動確認', '編集中です。他の画面に移動しますか？', self.font)
                # はいボタン
                yes_button = tk.Button(sub_win.frame, text='はい', width=8, font=(self.font, F_SIZE['S']))
                yes_button.bind('<1>', submit_yes)
                yes_button.pack(side=tk.LEFT, padx=5, pady=5)
                # いいえボタン
                no_button = tk.Button(sub_win.frame, text='いいえ', width=8, font=(self.font, F_SIZE['S']))
                no_button.bind('<1>', submit_no)
                no_button.pack(side=tk.LEFT, padx=5, pady=5)
            else:
                move(mv)
        
        # 既に存在している場合はメニューを破棄して再生成
        try:
            self.menu_frame.destroy()
        except:
            pass
        
        # 各メニュー生成
        self.menu_frame = tk.Frame(self, width=MENU_WIDTH, height=ROOT_HEIGHT)
        self.menu_frame.pack(anchor=tk.NW, side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)
        for i in MENU_ITEM:
            self.b = tk.Button(self.menu_frame, text=i, width=15, font=(self.font, F_SIZE['S']))
            self.b.bind('<1>', button_action)
            self.b.pack()

    # ---------------------------------------------------------------------------
    # メインフレーム生成
    # ---------------------------------------------------------------------------
    def main_create(self, w, h):
        
        # 既に存在している場合はメインフレームを破棄して再生成
        try:
            self.main_frame.destroy()
        except:
            pass
        self.main_frame = tk.Frame(self, width=w, height=h)
        self.main_frame.pack(anchor=tk.CENTER, side=tk.TOP, padx=5, pady=5, fill=tk.BOTH)
    
    # ---------------------------------------------------------------------------
    # 画面遷移
    # 
    # 各画面ごとの処理を記載．
    # ---------------------------------------------------------------------------
    # ホーム画面 
    # ---------------------------------------------------------------------------
    def home(self):
        
        # ファイル出力
        def submit_output(event):
            # ok
            def submit_ok(event):
                sub_win.destroy()
                
            # 項目指定確認
            if self.main_tree.focus().isdigit():
                memo = db.select_memo_one(self.main_tree.focus())
                self.output_file(memo[0][1], memo[0][3])
            else:
                # サブウィンドウ
                sub_win = sw.SubWindow('エラー', '出力する項目を指定してください', self.font)
                ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
                ok_button.bind('<1>', submit_ok)
                ok_button.pack(side=tk.LEFT, padx=5, pady=5)
                

        # 編集画面へ
        def submit_update(event):
            # ok
            def submit_ok(event):
                sub_win.destroy()
            
            # 項目指定確認
            if self.main_tree.focus().isdigit():
                memo = db.select_memo_one(self.main_tree.focus())
                self.update_memo(memo[0])
            else:
                # サブウィンドウ
                sub_win = sw.SubWindow('エラー', '編集項目を指定してください', self.font)
                ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
                ok_button.bind('<1>', submit_ok)
                ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 削除
        def submit_delete(event):
            # はい(データを削除して戻る)
            def submit_yes(event):
                # ok
                def submit_ok(event):
                    sub_sub_win.destroy()
                db.delete_memo(self.main_tree.focus())
                self.home()
                sub_win.destroy()
                sub_sub_win = sw.SubWindow('削除成功', '削除しました！', self.font)
                ok_button = tk.Button(sub_sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
                ok_button.bind('<1>', submit_ok)
                ok_button.pack(side=tk.LEFT, padx=5, pady=5)
            
            # いいえ
            def submit_no(event):
                sub_win.destroy()
            
            # ok
            def submit_ok(event):
                sub_win.destroy()
            
            # 項目を指定している場合のみ削除確認
            if self.main_tree.focus().isdigit():
                # Yes/Noウィンドウ
                sub_win = sw.SubWindow('削除確認', '削除しますか？', self.font)
                # はいボタン
                yes_button = tk.Button(sub_win.frame, text='はい', width=8, font=(self.font, F_SIZE['S']))
                yes_button.bind('<1>', submit_yes)
                yes_button.pack(side=tk.LEFT, padx=5, pady=5)
                # いいえボタン
                no_button = tk.Button(sub_win.frame, text='いいえ', width=8, font=(self.font, F_SIZE['S']))
                no_button.bind('<1>', submit_no)
                no_button.pack(side=tk.LEFT, padx=5, pady=5)
            else:
                # サブウィンドウ
                sub_win = sw.SubWindow('エラー', '削除する項目を指定してください', self.font)
                ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
                ok_button.bind('<1>', submit_ok)
                ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 編集中フラグ設定
        self.edit_flag = False

        # 機能ラベル
        self.main_create(MAIN_WIDTH, ROOT_HEIGHT)
        self.label_menuname = tk.Label(self.main_frame, text=MENU_ITEM[0], width=15, font=(self.font, F_SIZE['L']))
        self.label_menuname.pack(padx=5, pady=15)
        
        # ツリービュー
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack()
        self.main_tree = ttk.Treeview(self.tree_frame, padding=5, height=12)
        self.main_tree["columns"] = (1, 2, 3)
        self.main_tree["show"] = 'headings'
        self.main_tree.column(1, width=100)
        self.main_tree.column(2, width=100)
        self.main_tree.column(3, width=400)
        self.main_tree.heading(1, text="タイトル")
        self.main_tree.heading(2, text="カテゴリ")
        self.main_tree.heading(3, text="本文(抜粋)")
        self.main_tree_style = ttk.Style()
        self.main_tree_style.configure("Treeview", font=(self.font, F_SIZE['S']))
        self.main_tree_style.configure("Treeview.Heading", font=(self.font, F_SIZE['M'], tk.font.BOLD))
        
        # ツリースクロール
        self.main_scroll = tk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.main_tree.yview)
        self.main_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_tree['yscrollcommand'] = self.main_scroll.set
        
        # アイテムの取得＆挿入
        # SQLからアイテム取得
        for i in db.select_memo():
            text = i[3].replace('\n', ' ')
            self.main_tree.insert('', tk.END, iid=i[0], values=(i[1], i[2], text[0:30]))
        self.main_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 出力/編集/削除
        self.edit_frame = tk.Frame(self.main_frame)
        self.edit_frame.pack(padx=5, pady=5)
        self.button_output = tk.Button(self.edit_frame, text='出力', width=8, font=(self.font, F_SIZE['S']))
        self.button_output.bind('<1>', submit_output)
        self.button_output.pack(side=tk.LEFT, padx=15, pady=5)
        self.button_update = tk.Button(self.edit_frame, text='編集', width=8, font=(self.font, F_SIZE['S']))
        self.button_update.bind('<1>', submit_update)
        self.button_update.pack(side=tk.LEFT, padx=15, pady=5)
        self.button_delete = tk.Button(self.edit_frame, text='削除', width=8, font=(self.font, F_SIZE['S']))
        self.button_delete.bind('<1>', submit_delete)
        self.button_delete.pack(side=tk.LEFT, padx=15, pady=5)
        print(self.main_tree.focus())

    # カテゴリ別表示，および検索機能
    # -> 今後実装予定

    # ---------------------------------------------------------------------------
    # 登録画面
    # ---------------------------------------------------------------------------
    def insert_memo(self):
        
        # 登録してサブウィンドウを表示
        def submit_create(event):
            def submit_ok(event):
                sub_win.destroy()
                self.home()
            
            title = str(self.memo_title.get())
            # タイトルが1文字以上20文字以下の場合のみ登録処理
            if len(title) < 1 :
                sub_win = sw.SubWindow('登録失敗', 'タイトルを入力してください', self.font)
            elif len(title) > 20:
                sub_win = sw.SubWindow('登録失敗', 'タイトルは20文字以下で指定してください', self.font)
            else:
                c_id = db.select_category_id(self.combo_category.get())
                memo = [title, c_id[0][0], self.memo_input.get('1.0', tk.END)]
                db.insert_memo(memo)
                # サブウィンドウ
                sub_win = sw.SubWindow('登録完了', 'メモを登録しました！', self.font)
            ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
            ok_button.bind('<1>', submit_ok)
            ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 編集中フラグ設定
        self.edit_flag = True

        # 機能ラベル
        self.main_create(MAIN_WIDTH, ROOT_HEIGHT)
        self.label_menuname = tk.Label(self.main_frame, text=MENU_ITEM[1], width=15, font=(self.font, F_SIZE['L']))
        self.label_menuname.pack(padx=5, pady=15)
        self.make_memo_frame()
        
        # 登録ボタン
        self.submit_create = tk.Button(self.main_frame, text='登録', width=15, font=(self.font, F_SIZE['S']))
        self.submit_create.bind('<1>', submit_create)
        self.submit_create.pack(padx=5, pady=15)

    # ---------------------------------------------------------------------------
    # 編集画面 
    # ---------------------------------------------------------------------------
    def update_memo(self, memo):
        
        # 登録してサブウィンドウを表示
        def submit_update(event):
            def submit_ok(event):
                sub_win.destroy()
                self.home()
        
            title = str(self.memo_title.get())
            # タイトルが1文字以上20文字以下の場合のみ登録処理
            if len(title) < 1 :
                sub_win = sw.SubWindow('更新失敗', 'タイトルを入力してください', self.font)
            elif len(title) > 20:
                sub_win = sw.SubWindow('更新失敗', 'タイトルは20文字以下で指定してください', self.font)
            else:
                c_id = db.select_category_id(self.combo_category.get())
                update = [title, c_id[0][0], self.memo_input.get('1.0', tk.END), memo[0]]
                db.update_memo(update)
                sub_win = sw.SubWindow('更新完了', 'メモを更新しました！', self.font)
            ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
            ok_button.bind('<1>', submit_ok)
            ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 編集中フラグ設定
        self.edit_flag = True

        # 機能ラベル
        self.main_create(MAIN_WIDTH, ROOT_HEIGHT)
        self.label_menuname = tk.Label(self.main_frame, text='メモ編集', width=15, font=(self.font, F_SIZE['L']))
        self.label_menuname.pack(padx=5, pady=15)
        self.make_memo_frame()
        self.memo_title.insert(tk.END, memo[1])
        self.memo_input.insert(tk.END, memo[3])
        
        # 登録ボタン
        self.submit_update = tk.Button(self.main_frame, text='更新', width=15, font=(self.font, F_SIZE['S']))
        self.submit_update.bind('<1>', submit_update)
        self.submit_update.pack(padx=5, pady=15)

    # ---------------------------------------------------------------------------
    # メモ枠組 
    # ---------------------------------------------------------------------------
    def make_memo_frame(self):
        
        # タイトル
        self.title_frame = tk.Frame(self.main_frame)
        self.title_frame.pack(padx=45, pady=15, fill=tk.BOTH)
        self.label_memo_title = tk.Label(self.title_frame, text='タイトル(1～20文字)', font=(self.font, F_SIZE['S']))
        self.label_memo_title.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.memo_title = tk.Entry(self.title_frame, font=(self.font, F_SIZE['S']))
        self.memo_title.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        # カテゴリ
        self.label_memo_category = tk.Label(self.title_frame, text='カテゴリ', font=(self.font, F_SIZE['S']))
        c_name = []
        for i in db.select_category():
            c_name.append(i[1])
        self.combo_category = ttk.Combobox(self.title_frame, values=c_name, width=15, \
            state='readonly', font=(self.font, F_SIZE['S']))
        self.combo_category.current(0)
        # 右から順にpack()
        self.combo_category.pack(side=tk.RIGHT, fill=tk.X, padx=5)
        self.label_memo_category.pack(side=tk.RIGHT, fill=tk.X, padx=5)
        
        # 本文
        self.memo_frame = tk.Frame(self.main_frame)
        self.memo_frame.pack()
        self.memo_input = tk.Text(self.memo_frame, height=12, font=(self.font, F_SIZE['S']))
        
        # 本文スクロール
        self.memo_scroll = tk.Scrollbar(self.memo_frame, orient=tk.VERTICAL, command=self.memo_input.yview)
        self.memo_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.memo_input['yscrollcommand'] = self.memo_scroll.set
        self.memo_input.pack()

    # ---------------------------------------------------------------------------
    # カテゴリ編集 
    # ---------------------------------------------------------------------------
    def category_edit(self):
        
        # カテゴリ登録
        def submit_insert(event):
            def submit_ok(event):
                sub_win.destroy()
            
            c_name = str(self.entry_insert.get())
            
            # タイトルが1文字以上20文字以下の場合のみ登録処理
            if len(c_name) < 1 :
                sub_win = sw.SubWindow('登録失敗', 'カテゴリ名を入力してください', self.font)
            elif len(c_name) > 20:
                sub_win = sw.SubWindow('登録失敗', 'カテゴリ名は20文字以下で指定してください', self.font)
            else:
                db.insert_category(c_name)
                sub_win = sw.SubWindow('登録完了', 'カテゴリを登録しました！', self.font)
                self.category_edit()
            
            ok_button = tk.Button(sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
            ok_button.bind('<1>', submit_ok)
            ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        # カテゴリ削除
        def submit_delete(event):
            # はい
            def submit_yes(event):
                def submit_ok(event):
                    sub_sub_win.destroy()
                    self.category_edit()
                sub_win.destroy()
                c_id = db.select_category_id(self.combo_delete.get())
                # カテゴリなしは削除できないよう設定
                if c_id[0][0] == 1:
                    sub_sub_win = sw.SubWindow('削除失敗', 'カテゴリなしは削除できません', self.font)
                else:
                    db.delete_category(c_id[0][0])
                    sub_sub_win = sw.SubWindow('削除成功', 'カテゴリの削除に成功しました！', self.font)
                ok_button = tk.Button(sub_sub_win.frame, text='OK', width=8, font=(self.font, F_SIZE['S']))
                ok_button.bind('<1>', submit_ok)
                ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        
            # いいえ
            def submit_no(event):
                sub_win.destroy()

            # Yes/Noウィンドウ
            sub_win = sw.SubWindow('削除の確認', '本当にカテゴリを削除しますか？\n(該当カテゴリのメモも削除されます)', self.font)
            # はいボタン
            yes_button = tk.Button(sub_win.frame, text='はい', width=8, font=(self.font, F_SIZE['S']))
            yes_button.bind('<1>', submit_yes)
            yes_button.pack(side=tk.LEFT, padx=5, pady=5)
            # いいえボタン
            no_button = tk.Button(sub_win.frame, text='いいえ', width=8, font=(self.font, F_SIZE['S']))
            no_button.bind('<1>', submit_no)
            no_button.pack(side=tk.LEFT, padx=5, pady=5)    
        
        # 編集中フラグ設定
        self.edit_flag = False

        # 機能ラベル
        self.main_create(MAIN_WIDTH, ROOT_HEIGHT)
        self.label_menuname = tk.Label(self.main_frame, text=MENU_ITEM[2], width=15, font=(self.font, F_SIZE['L']))
        self.label_menuname.pack(padx=5, pady=15)
        
        # カテゴリ登録
        self.ins_frame = tk.Frame(self.main_frame)
        self.ins_frame.pack(padx=5, pady=15)
        self.label_insert = tk.Label(self.ins_frame, text='カテゴリ登録', font=(self.font, F_SIZE['S']))
        self.label_insert.pack(side=tk.LEFT, padx=5, pady=5)
        self.entry_insert = tk.Entry(self.ins_frame, width=17, font=(self.font, F_SIZE['S']))
        self.entry_insert.pack(side=tk.LEFT, padx=5, pady=5)
        self.button_insert = tk.Button(self.ins_frame, text='登録', width=8, font=(self.font, F_SIZE['S']))
        self.button_insert.bind('<1>', submit_insert)
        self.button_insert.pack(side=tk.LEFT, padx=5, pady=5)
        
        # カテゴリ削除
        self.del_frame = tk.Frame(self.main_frame)
        self.del_frame.pack(padx=5, pady=15)
        self.label_delete = tk.Label(self.del_frame, text='カテゴリ削除', font=(self.font, F_SIZE['S']))
        self.label_delete.pack(side=tk.LEFT, padx=5, pady=5)
        c_name = []
        for i in db.select_category():
            c_name.append(i[1])
        self.combo_delete = ttk.Combobox(self.del_frame, values=c_name, width=15, \
            state='readonly', font=(self.font, F_SIZE['S']))
        self.combo_delete.current(0)
        self.combo_delete.pack(side=tk.LEFT, padx=5, pady=5)
        self.button_delete = tk.Button(self.del_frame, text='削除', width=8, font=(self.font, F_SIZE['S']))
        self.button_delete.bind('<1>', submit_delete)
        self.button_delete.pack(side=tk.LEFT, padx=5, pady=5)

    # ---------------------------------------------------------------------------
    # アプリ設定
    # ---------------------------------------------------------------------------
    def app_config(self):
        
        # コンフィグ変更の確認
        def submit_config(event):
            # はい
            def submit_yes(event):
                self.config_write(self.combo_charset.get(), self.combo_font.get())
                self.menu_create()
                self.app_config()
                sub_win.destroy()

            # いいえ
            def submit_no(event):
                sub_win.destroy()

            # Yes/Noウィンドウ
            sub_win = sw.SubWindow('変更確認', '設定を変更しますか？', self.font)
            # はいボタン
            yes_button = tk.Button(sub_win.frame, text='はい', width=8, font=(self.font, F_SIZE['S']))
            yes_button.bind('<1>', submit_yes)
            yes_button.pack(side=tk.LEFT, padx=5, pady=5)
        
            # いいえボタン
            no_button = tk.Button(sub_win.frame, text='いいえ', width=8, font=(self.font, F_SIZE['S']))
            no_button.bind('<1>', submit_no)
            no_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 編集中フラグ設定
        self.edit_flag = False

        # 機能ラベル
        self.main_create(MAIN_WIDTH, ROOT_HEIGHT)
        self.label_menuname = tk.Label(self.main_frame, text=MENU_ITEM[3], width=15, font=(self.font, F_SIZE['L']))
        self.label_menuname.pack(padx=5, pady=15)
        
        # 文字コード設定
        self.charset_frame = tk.Frame(self.main_frame)
        self.charset_frame.pack()
        self.label_charset = tk.Label(self.charset_frame, text='出力文字コード', width=15, font=(self.font, F_SIZE['S']))
        self.label_charset.pack(side=tk.LEFT, padx=5, pady=5)
        self.combo_charset = ttk.Combobox(self.charset_frame, values=CHAR_SET, width=15, \
            state='readonly', font=(self.font, F_SIZE['S']))
        self.combo_charset.current(0)
        self.combo_charset.pack(side=tk.LEFT, padx=5, pady=5)
        self.label_charset_now = tk.Label(self.charset_frame, anchor=tk.W, text=('現在の設定：%s' % self.charset), \
            width=30, font=(self.font, F_SIZE['S']))
        self.label_charset_now.pack(side=tk.LEFT, padx=5, pady=5)

        # フォント設定
        self.font_frame = tk.Frame(self.main_frame)
        self.font_frame.pack()
        self.label_font = tk.Label(self.font_frame, text='フォント', width=15, font=(self.font, F_SIZE['S']))
        self.label_font.pack(side=tk.LEFT, padx=5, pady=5)
        self.combo_font = ttk.Combobox(self.font_frame, values=CHAR_FONT, width=15, \
            state='readonly', font=(self.font, F_SIZE['S']))
        self.combo_font.current(0)
        self.combo_font.pack(side=tk.LEFT, padx=5, pady=5)
        self.label_charset_now = tk.Label(self.font_frame, anchor=tk.W, text=('現在の設定：%s' % self.font), \
            width=30, font=(self.font, F_SIZE['S']))
        self.label_charset_now.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 決定
        self.submit_config = tk.Button(self.main_frame, text='決定', width=15, font=(self.font, F_SIZE['S']))
        self.submit_config.bind('<1>', submit_config)
        self.submit_config.pack(padx=5, pady=5)

# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.title(TITLE)
    root.resizable(0, 0)
    # 初期表示位置指定
    sx = int(root.winfo_screenwidth()/2)
    sy = int(root.winfo_screenheight()/2)
    root.geometry("%sx%s+%s+%s" % (ROOT_WIDTH, ROOT_HEIGHT, int(sx - ROOT_WIDTH/2), int(sy - ROOT_HEIGHT/2)))
    # 開始
    app = MemoPad(master=root)
    app.mainloop()
