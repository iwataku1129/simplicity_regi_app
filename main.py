# coding:utf-8
import configparser
import csv
import datetime
import json
import os
import PySimpleGUI as sg
import socket
from controller.logger_controll import f_set_logger_conf


# -------------------------------------------------------------------------------
# Name:                 csv登録
# -------------------------------------------------------------------------------
def f_post_csv(t_now, t_id, t_staff_name, t_pay, t_pay_tax, t_price, t_cash, arr_goods, arr_goods_cnt, host):
    try:
        os.mkdir(f"./export/{t_now.date()}")
    except FileExistsError as e:
        pass
    t_filename = f"./export/{t_now.date()}/【レジApp】売上データ_{t_now.date()}.csv"

    if not (os.path.exists(t_filename)):
        head = ["日時","予約番号","支払方法","手数料(%)","料金","受領金額","おつり","手数料(円)","登録者","登録PC"]
        for goods in arr_goods:
            head.append(goods[0])
        with open(t_filename, "w", newline="", encoding="utf-16") as f:
            writer = csv.writer(f, dialect="excel-tab")
            writer.writerow(head)

    column = [t_now, t_id, t_pay, t_pay_tax, t_price, t_cash, t_cash-t_price, t_price*t_pay_tax/100, t_staff_name, host ]
    for goods_cnt in arr_goods_cnt:
        column.append(goods_cnt)
    with open(t_filename, "a", newline="", encoding="utf-16") as f:
        writer = csv.writer(f, dialect="excel-tab")
        writer.writerow(column)


# -------------------------------------------------------------------------------
# Name:                 Main関数
# -------------------------------------------------------------------------------
def f_main_page(logger):
    # 店舗別可変値
    sg.theme('Green')

    # Config取得
    config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    config.read("./config/設定ファイル.ini")
    keep_on_top = eval(config.get("基本設定", "最前面表示"))
    no_titlebar = eval(config.get("基本設定", "タイトル非表示"))

    arr_pay = json.loads(config.get("レジ設定", "支払方法"))
    t_pay_init = json.loads(config.get("レジ設定", "支払方法初期値"))
    arr_goods = json.loads(config.get("レジ設定", "商品"))

    # リスト用変数作成
    paylist = []
    for i in arr_pay:
        paylist.append(i[0])

    # 可変画面レイアウト作成
    if len(arr_goods) > 9 or len(arr_goods) <= 0:
        logger.error("[レジApp]商品登録数は「1」～「9」です。")
        return
    flex_layout1 = []
    arr_goods_cnt = []
    for cnt,i in enumerate(arr_goods):
        flex_layout1.append([sg.Text(f'●{i[0]}', font=('Noto Serif CJK JP',18))])
        flex_layout1.append([sg.Button(' + ', key=f'goods_plus_{cnt}', size=(8,2)), sg.Button(' - ', key=f'goods_minus_{cnt}', size=(8,2)), sg.InputText(0, key=f'goods_{cnt}_cnt', size=(8,3), font=('Noto Serif CJK JP',18), text_color='#3366ee', readonly=True)])
        arr_goods_cnt.append(0)

    # 画面レイアウト作成
    layout1 = [
        [sg.Text(f"【レジアプリ】", font=('Noto Serif CJK JP',12))],
        [sg.Text('●受付担当者：', font=('Noto Serif CJK JP',18)), sg.InputText("", key='staff_name', size=(8,3), font=('Noto Serif CJK JP',18), background_color='yellow', text_color='#3366ee')],
    ]
    layout1.extend(flex_layout1)
    layout1.extend([
        [sg.Text('', font=('Noto Serif CJK JP',2))],
        [sg.Text('●料金', font=('Noto Serif CJK JP',18))],
        [sg.InputText(0, key='price', size=(15,3), font=('Noto Serif CJK JP',18), text_color='#3366ee', readonly=True),sg.Text('円')],
        [sg.Text('', font=('Noto Serif CJK JP',2))],
        [sg.Text('●お支払い/おつり', font=('Noto Serif CJK JP',18))],
        [sg.Text('受領金額：', justification='c', pad=((0,0),(0,0))), sg.InputText(0, key='cash', size=(8,3), font=('Noto Serif CJK JP',18), background_color='yellow', text_color='#3366ee'), sg.Button('円 (確定)', key='cash_button'), sg.InputText(0, key='exchange', size=(8,3), font=('Noto Serif CJK JP',18), text_color='#3366ee', readonly=True),sg.Text('円')],
        [sg.Button(' +1k ', key='p_1k', pad=((80,0),(0,0))), sg.Button(' +1m ', key='p_1m'), sg.Text(' '), sg.Button(' = ', key='same_price'), sg.Text(' '), sg.Button(' -1m ', key='m_1m'), sg.Button(' -1k ', key='m_1k')],
        [sg.Combo(values=paylist, default_value=t_pay_init, size=(25, 1), key='pay', pad=((80,0),(0,0)))],
        [sg.Text('予約番号：'), sg.InputText("", key='id', size=(15,3), font=('Noto Serif CJK JP',18), background_color='yellow', text_color='#3366ee'), ],   # sg.Button('番号生成', key='mk_id_button')
        [sg.Text('', font=('Noto Serif CJK JP',2))],
        [sg.Text('●登録/リセット', font=('Noto Serif CJK JP',18))],
        [sg.Button('登録', key='submit', size=(11,2)), sg.Button('リセット\n(3回クリック)', key='reset', size=(11,2)),sg.Text(" ")],
        [sg.Text('警告：'), sg.InputText("", key='warn_message', text_color='red', readonly=True),sg.Text(" ")],
        [sg.Text('情報：'), sg.InputText("", key='success_message', text_color='green', readonly=True)],
        [sg.Text('', font=('Noto Serif CJK JP',3))]
    ])
    layout2 = [
        [sg.Exit(button_color=('white', 'Darkred'), key='-QUIT-', pad=((0,0),(20,0)))]
    ]
    # ウィンドウオブジェクトの作成
    layout = [[sg.TabGroup([[sg.Tab('Main', layout1), sg.Tab('Settings', layout2)]])]]
    window = sg.Window(f'[レジApp]Main Window', layout, no_titlebar=no_titlebar, grab_anywhere=True, resizable=False, auto_size_text=True, auto_size_buttons=True, keep_on_top=keep_on_top, icon="favicon.ico", element_padding=(1, 1))

    # イベントのループ
    t_id = ""
    t_price = 0
    t_cash = 0
    t_reset_cnt = 0
    reset_flg = False
    t_success_message = ""
    t_warn_message = ""
    host = socket.gethostname()
    while True:
        # イベントの読み込み
        event, values = window.read()
        logger.debug(f"event:{event}")

        # event発生時常時更新
        if event != None:
            # 予約番号(unique)生成
            if event != "reset":
                t_reset_cnt = 0
                if t_id == "":
                    t_id = datetime.datetime.now()
                    t_id = t_id.strftime('%H %M %S')
                    window['id'].update(t_id)

            # 受領額常時計算 (入力欄更新はeventと認識されない為、event発生時常時更新)
            t_cash = values['cash']
            try:
                t_cash = int(t_cash)
            except:
                t_cash = 0
            window['cash'].update(t_cash)
        else:
            break
           
        # 個数変更時 売価更新
        if "goods_plus_" in event or "goods_minus_" in event:
            i = int(event[event.rfind("_")+1:])
            if "_plus_" in event:
                arr_goods_cnt[i] = arr_goods_cnt[i] + 1
                t_price += arr_goods[i][1]
            elif "_minus_" in event and arr_goods_cnt[i] > 0:
                arr_goods_cnt[i] = arr_goods_cnt[i] - 1
                t_price -= arr_goods[i][1]
            window[f'goods_{i}_cnt'].update(arr_goods_cnt[i])
            window['price'].update("{:,d}".format(t_price))
            window['cash'].update(t_cash)
            window['exchange'].update("{:,d}".format(t_cash - t_price))
        # 受領額・お釣り 計算
        elif event in ("p_1k", "p_1m", "same_price", "m_1k", "m_1m", "cash_button"):
            if event in ("p_1k"):
                t_cash = int(t_cash) + 1000
            elif event in ("p_1m"):
                t_cash = int(t_cash) + 100
            elif event in ("m_1k"):
                t_cash = int(t_cash) - 1000
            elif event in ("m_1m"):
                t_cash = int(t_cash) - 100
            elif event in ("same_price"):
                t_cash = t_price
            if t_cash < 0:
                t_cash = 0
            window['cash'].update(t_cash)
            window['exchange'].update("{:,d}".format(t_cash - t_price))
        elif event == "reset":
            t_reset_cnt += 1
            if t_reset_cnt >= 3:
                reset_flg = True
        elif event == "submit":
            t_id = values['id']
            t_staff_name = values['staff_name']
            t_pay = values['pay']
            if not t_id or (t_cash == "" or t_cash == 0) or (not t_pay in paylist):
                t_success_message = ""
                t_warn_message = "予約番号・支払方法または受領金額が登録されていません"
                logger.debug(f"warn:{t_warn_message}")
                window['success_message'].update(t_success_message)
                window['warn_message'].update(t_warn_message)
            elif t_price > t_cash:
                t_success_message = ""
                t_warn_message = "受領金額が足りません"
                logger.debug(f"warn:{t_warn_message}")
                window['success_message'].update(t_success_message)
                window['warn_message'].update(t_warn_message)
            else:
                # 手数料取得
                t_pay_tax = 0
                for i in arr_pay:
                    if i[0] == t_pay:
                        t_pay_tax = i[1]
                        break
                # table登録
                try:
                    t_now = datetime.datetime.today()
                    logger.info(f"dt:{t_now} - 予約番号:{t_id} - 支払方法:{t_pay} - 手数料:{t_pay_tax} - 料金:{t_price} - 受領金額:{t_cash} - 登録者:{t_staff_name} - host:{host}")
                    f_post_csv(t_now, t_id, t_staff_name, t_pay, t_pay_tax, t_price, t_cash, arr_goods, arr_goods_cnt, host)
                    logger.info(" =>登録完了")
                    t_success_message = f"登録完了! dt:{t_now} - 予約番号:{t_id}"
                    t_warn_message = ""
                    reset_flg = True
                except PermissionError:
                    logger.info(f" =>登録失敗:ファイルが開かれています。")
                    t_success_message = ""
                    t_warn_message = f"登録失敗:ファイルが開かれています。再実行してください。"
                except Exception as e:
                    logger.info(f" =>登録失敗:{e}")
                    t_success_message = ""
                    t_warn_message = f"登録失敗:{e}"
                window['success_message'].update(t_success_message)
                window['warn_message'].update(t_warn_message)
        elif event in (sg.WIN_CLOSED, '-QUIT-'):
            break

        # 初期化処理
        if reset_flg:
            t_id = ""
            t_price = 0
            t_cash = 0
            t_reset_cnt = 0
            t_success_message = ""
            t_warn_message = ""
            window['id'].update(t_id)
            window['price'].update(t_price)
            window['cash'].update(t_cash)
            window['exchange'].update(0)
            window['success_message'].update(t_success_message)
            window['warn_message'].update(t_warn_message)
            for i in range(len(arr_goods_cnt)):
                arr_goods_cnt[i] = 0
                window[f'goods_{i}_cnt'].update(0)
            if not t_pay_init:
                window['pay'].update("")
            reset_flg = False

    # ウィンドウ終了処理
    window.close()


# -------------------------------------------------------------------------------
# Name:                 Main処理
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        os.mkdir(f"./log")
    except FileExistsError as e:
        pass

    # Logコンフィグ設定
    logger = f_set_logger_conf(logl_lvl=10, filename=f'./log/レジ_{datetime.date.today()}.log')

    logger.info("[レジApp]起動")
    f_main_page(logger)