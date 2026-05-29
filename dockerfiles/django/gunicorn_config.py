# バインド設定
bind = '0.0.0.0:8000'

# ワーカー設定
workers = 5
timeout = 300

# プロセス設定 マスタープロセスがアプリを先に読み込んでからworkerをコピーする
preload_app = True