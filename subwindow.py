# -*- coding: utf-8 -*-
# tkinter
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font

# アプリ定数
SUB_WIDTH = 300
SUB_HEIGHT = 160

# ---------------------------------------------------------------------------
# SubWindow
#
# 確認ウィンドウ用クラス
# ボタンを押した場合，呼び出し元に従うまたはdestroy()を実行．
# ボタンは複数配置可能．(例：はい/いいえボタン)
# ---------------------------------------------------------------------------
class SubWindow(tk.Toplevel):
    def __init__(self, title, mess, font, master=None):
        super().__init__(master)

        # ウィンドウタイトル
        self.title(title)
        sx = int(self.winfo_screenwidth()/2)
        sy = int(self.winfo_screenheight()/2)
        self.resizable(0, 0)
        self.geometry("%sx%s+%s+%s" % (SUB_WIDTH, SUB_HEIGHT, int(sx - SUB_WIDTH/2), int(sy - SUB_HEIGHT/2)))
            
        self.transient(master)
        self.grab_set()
        # メッセージ＆フレーム生成
        self.label_message = tk.Label(self, text=mess, font=(font, 10))
        self.label_message.pack(padx=5, pady=15)
        self.frame = tk.Frame(self)
        self.frame.pack(side=tk.BOTTOM, padx=5, pady=15)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('SubWindow')
    app = SubWindow(title='title', mess='mess', font='メイリオ', master=root)
    app.mainloop()