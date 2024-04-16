from time import sleep
import time
from datetime import datetime
import nfc
import json
import tkinter
import subprocess
import threading
import os

# タッチされたとき，時間を非表示にするフラグ
Flg = [1]
Flg[0] = False

# スレッド作成関数(並列処理)
def Thread_Event():
    th1 = threading.Thread(target=print_datetime)# スレッドインスタンス生成(print_datetime)
    th2 = threading.Thread(target=read_nfc)# スレッドインスタンス生成(read_nfc)
    th1.start()# スレッドスタート
    th2.start()# スレッドスタート

# 日時表示
def print_datetime():
    while True:
        if Flg[0]:
            sleep(0.01)
            continue
        global now
        now_h=datetime.now().hour
        now_s=datetime.now().second
        now_m=datetime.now().minute
        if len(str(now_h)) == 1:
            h = '0' + str(now_h)
        else:
            h = str(now_h)
        if len(str(now_m)) == 1:
            m = '0' + str(now_m)
        else:
            m = str(now_m)
        if len(str(now_s)) == 1:
            s = '0' + str(now_s)
        else:
            s = str(now_s)
        now_time = '　現在時刻：' +h+":"+m+":"+s
        display_label["text"] = f'　出席管理システム\n\n{now_time}\n\n\n　タッチ\n  ↓'
        sleep(1)

# タッチされた時の処理
def on_connect(tag):
    idm, pmm = tag.polling(system_code=0xfe00)
    tag.idm, tag.pmm, tag.sys = idm, pmm, 0xfe00

    service_code = 0x1a8b
    sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
    bc1 = nfc.tag.tt3.BlockCode(0, service=0) # 学籍番号のブロックコード
    bc2 = nfc.tag.tt3.BlockCode(1, service=0) # 氏名のブロックコード
    data = tag.read_without_encryption([sc], [bc1, bc2])

    # カードのすべての情報
    # print ('  ' + '\n  '.join(tag.dump()))

    number = data[2:8].decode("utf-8") # 学籍番号
    name = data[16:32].decode("shift_jis") # 氏名(半角カタカナ)

    # JSONファイルの読み込み
    try:
        with open('./data.json', 'r') as json_file:
            data = json.load(json_file) # data配列に代入
    except FileNotFoundError: # JSONファイルが存在しない場合、新しいリストを作成
        data = []

    # 新しいデータを作成
    new_data = {
        "number": number,
        "timestamp": str(datetime.now().replace(microsecond=0))  # 現在のタイムスタンプを文字列に変換
    }

    # data配列に新しいデータを追加
    data.append(new_data)

    # JSONファイルにデータを書き込み
    with open('./data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # 学籍番号
    # print ("Number: " + number)

    Flg[0] = True

    # ウィンドウに表示
    try:
        with open (f'./text/{number}.txt', 'r', encoding='UTF-8') as txt:
            display_label["text"] = txt.read()
    except:
        display_label["text"] = f"出席しました！\n\n学籍番号：{number}\n\n名前：{name}"

    
    sound = os.system(f"mpg321 ./sound/{number}.mp3 2>&1")  # 音鳴らす（正常時）
    if sound != 0:
        subprocess.Popen(['mpg321','./sound/sample.mp3'], stdout=open('/dev/null', 'w'))  # 音鳴らす（正常時）
        
# NFC
def read_nfc():
    # USBからNFCリーダーを認識
    with nfc.ContactlessFrontend('usb') as clf:
        while True:
            # 例外処理
            try:
                clf.connect(rdwr={'on-connect': on_connect})  # カードがタッチされたら実行(on_connect関数)
            except:
                print('Error')
                display_label["text"] ="\n\n\n　　読み込みエラー"
                Flg[0] = True
                subprocess.Popen(['mpg321', './sound/error.mp3'], stdout=open('/dev/null', 'w'))  # 音鳴らす（異常時）
            sleep(3)
            Flg[0] = False

if __name__ == '__main__':
    #debug = input("デバッグモード(入力=debug)：")
    root = tkinter.Tk() # ウィンドウを作成
    root.title("Attendance_System") # ウィンドウのタイトル
    root.configure(bg="black")
    # root.geometry("1280x1024") # ウィンドウの画面サイズ
    #if debug == 'debug':
    #    root.attributes("-zoomed", "1") # ウィンドウの画面最大化(1)
    #else :
    #    root.attributes("-fullscreen", True) # ウィンドウの画面全画面
    root.attributes("-fullscreen", True)
    display_label = tkinter.Label(root, text="", bg="black", fg="white", font=("MSゴシック", "80", "bold")) # フォント指定
    display_label.grid(row=1, column=0) # ウィンドウを動かす

    Thread_Event() # スレッド作成関数(並列処理)
    root.mainloop()