# coding:utf-8
import logging


# -------------------------------------------------------------------------------
# Name:                 [Set]コネクション作成関数
# logl_lvl:           0:全部, 10:DEBUG, 20:Info, 30:Warning, 40,Error, 50,CRITICAL
# filename:           出力Path + FileName (exa.'./Log/info.log')
# logger(return):     logger
# -------------------------------------------------------------------------------
def f_set_logger_conf(logl_lvl, filename):
    # ログの出力名を設定
    t_logger = logging.getLogger(__name__)

    # ログレベルの設定
    t_logger.setLevel(logl_lvl)  # 0:全部, 10:DEBUG, 20:Info, 30:Warning, 40,Error, 50,CRITICAL

    # ログのコンソール出力の設定
    t_sh = logging.StreamHandler()
    t_logger.addHandler(t_sh)

    # ログのファイル出力先を設定
    t_fh = logging.FileHandler(filename=filename, encoding='utf-8')
    t_logger.addHandler(t_fh)
 
    # ログの出力形式の設定
    t_formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
    t_fh.setFormatter(t_formatter)
    t_sh.setFormatter(t_formatter)

    return t_logger


# -------------------------------------------------------------------------------
# Name:                 [Set]Logメッセージセット
# logger_type:        logger + lvl (exa. logger.info)
#                          0:全部, 10:DEBUG, 20:Info, 30:Warning, 40,Error, 50,CRITICAL
# message:           表示 メッセージ
# -------------------------------------------------------------------------------
def f_set_logger(logger_type, message):
    logger_type(message)
    return


# -------------------------------------------------------------------------------
# Name:                 Main処理
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    # 変数定義
    t_logl_lvl = 10
    t_filename = "./test.log"

    # ログConfigセット
    t_logger = f_set_logger_conf(t_logl_lvl, t_filename)

    # ログ送信
    t_logger_type = t_logger.info
    t_message = "テスト送信"
    f_set_logger(t_logger_type, t_message)