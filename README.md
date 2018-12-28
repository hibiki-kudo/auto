# Twitter Autos
ツイッターに関わる部分の自動化をするためのプロジェクトです
## library
- selenium
- BeautifulSoup
- MeCab
- WordCloud
- matplotlib
- numpy
- pillow
- requests
- pandas
## description
### auto.py
ツイッター上の検索をして自動ファボ、リツイート、フォローを行う
### profile_morphological_analysis.py
単語の出現頻度を求めて、csv形式で結果を出力する
##search.py
ツイッター検索と検索ページのスクロールをする
### tweet.py
検索して得られるツイート情報をパースする
### tweet_analytics.py
ツイッターのアナリティクス情報を取得して、分析する。
### tweet_history.py
ユーザの過去のツイートを取得する関数
### user_scrape.py
ユーザのフォロワのプロフィール情報を抽出する
### word_cloud.py
過去のツイートの単語の出現頻度からワードクラウドを作成する