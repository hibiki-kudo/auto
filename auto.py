from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from search import TwitterSearch

# ウェブドライバーのディレクトリをexecutable_pathのところに設定してください
driver = webdriver.Firefox(executable_path="./geckodriver")


# ツイッターログイン関数
def login(user_name="", password="", email=""):
    driver.get("https://twitter.com/")
    sleep(2)  # 読み込み待ち時間

    driver.find_element_by_name("session[username_or_email]").send_keys(user_name)
    driver.find_element_by_name("session[password]").send_keys(password)
    driver.find_element_by_name("session[password]").send_keys(Keys.ENTER)
    sleep(2)  # 読み込み待ち時間

    # もしログインした際に乗っ取りアカウントだと判別された際に対応するための処理
    if driver.current_url != "https://twitter.com/":
        driver.find_element_by_id("challenge_response").send_keys(email)
        driver.find_element_by_id("challenge_response").send_keys(Keys.ENTER)
        sleep(3)  # 読み込み待ち時間


# ファボをおす関数
def favorite(tweet_id=""):
    driver.get("https://twitter.com/intent/favorite?tweet_id=" + tweet_id)
    # すでにファボを押しているか確認
    if "https://twitter.com/intent/favorite?tweet_id=" in driver.current_url:
        driver.find_element_by_name("commit").click()


# リツイートを押す関数
def retweet(tweet_id=""):
    driver.get("https://twitter.com/intent/retweet?tweet_id=" + tweet_id)
    # すでにリツイートを押しているか確認
    if "https://twitter.com/intent/retweet?tweet_id=" in driver.current_url:
        driver.find_element_by_name("commit").click()


# フォローをする関数
def follow(screen_name=""):
    driver.get("https://twitter.com/intent/user?screen_name=" + screen_name)
    # すでにフォローしているか確認(ここはページURIが変わらないためhtmlの要素が見つからないなら処理しないという形で実装)
    try:
        driver.find_element_by_id("follow_btn_form").click()
    except:
        pass


def main():
    user_name = ""  # ログインするときに入力するユーザーネーム
    password = ""  # ログインするときに入力するパスワード
    email = ""  # 乗っ取りと判断された際の対策用

    query = ""  # 検索内容

    # ログイン処理
    login(user_name=user_name, password=password, email=email)

    # 検索してツイート情報をもってくるためのクラスのインスタンス化
    tweets = TwitterSearch()

    # 検索処理
    tweets.search(query=query)

    # 検索して出てきたツイート全部にいいね、リツイート、フォローをするための処理
    while True:
        try:
            for tweet in tweets.tweets:
                # いいね
                # favorite(tweet_id=tweet.id)
                # sleep(3)  # それぞれサーバに負荷をかけないように待ち時間を設定
                # リツイート
                retweet(tweet_id=tweet.id)
                sleep(3)
                # フォロー
                follow(screen_name=tweet.user)
                sleep(3)

            # 検索ページをスクロールしてツイート情報を抜き取る
            tweets.scroll()

        # あまり良くないけどエラーが発生したら強制終了するようにした
        except:
            print("ファボ・リツイート・フォロー終了")
            break

    # ブラウザを閉じる
    driver.close()


if __name__ == "__main__":
    main()
