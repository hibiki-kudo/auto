import copy
import os
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from morphological_analysis import *

# アナリティクスを取得するためのログイン内容
user_name = ""
password = ""
email = ""

tweets_num = 0

base_file_path = "./csvファイル/"


# ツイッターログイン処理
def login():
    global tweets_num, driver
    driver = webdriver.Firefox(executable_path="./geckodriver")
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

    tweets_num = int(
        BeautifulSoup(driver.page_source, "html.parser").find("span", attrs={"class": "ProfileCardStats-statValue"})[
            "data-count"])


# ページスクロールして古いデータまで取得するための関数
def scroll_pages():
    global driver
    driver.get(f"https://analytics.twitter.com/user/{user_name}/tweets")
    sleep(2)
    try:
        for i in range(tweets_num // 10):  # ここの10はなんとなく
            before_html = driver.page_source
            driver.execute_script(f"window.scrollTo({i+1}, document.body.scrollHeight);")
            sleep(3)

            if len(before_html) == len(driver.page_source):
                print(len(before_html))
                print(len(driver.page_source))
                break

    except:
        print("スクロール終了")


# htmlから必要な要素を抜き取る処理
def scrape():
    tweets = BeautifulSoup(driver.page_source, "html.parser").find_all("li", attrs={
        "class": "topn-page tweet-activity-tweet-group"})

    info = []
    for tweet in tweets:
        info.append([copy.deepcopy(tweet.find("span", attrs={"class": "tweet-text"}).text),
                     copy.deepcopy(int(tweet.find("div", attrs={"class",
                                                                "tweet-activity-data impressions text-right col-md-1"}).text.replace(
                         ",", ""))),
                     copy.deepcopy(int(tweet.find("div", attrs={"class",
                                                                "tweet-activity-data metric text-right col-md-2"}).text.replace(
                         ",", ""))),
                     int(tweet.find("div", attrs={"class",
                                                  "tweet-activity-data metric text-right col-md-2"}).text.replace(
                         ",", "")) /
                     int(tweet.find("div", attrs={"class",
                                                  "tweet-activity-data impressions text-right col-md-1"}).text.replace(
                         ",", "")) * 100
                     ])

    return info


# CSV形式で保存する処理
def save_csv_tweet_analytics(csv_info, file_name):
    df = pd.DataFrame(csv_info, columns=["テキスト", "impressions", "engagements", "engagement rate"])
    df.to_csv(base_file_path + file_name)


# 昇順、降順に並び替えてCSVに保存する処理
def sort_engagement_rate(file_path, ascending_order=True, descending_order=True):
    if ascending_order:  # 降順(エンゲージ率が大きい順から0でないもの)
        select_range(file_path, "ascending_order.csv", True, 0.0, 0.0)

    if descending_order:  # 昇順(エンゲージ率が0のものだけ)
        select_range(file_path, "descending_order.csv", False, 100, 0.01)


# 取得したいエンゲージメント率の範囲を指定してCSVに保存できる関数
def select_range(file_path, save_file_name, reverse=True, top=100, bottom=0):
    '''
    :param file_path: もとファイル(my_analytics.csv),topとbottomは
    :param save_file_name: 保存先のファイルネーム
    :param reverse: 並び順(Trueならエンゲージ率の降順)
    :param top: エンゲージ率の範囲の最大(初期値 100%)
    :param bottom: エンゲージ率の範囲の最小(初期値 0%)
    '''
    file = pd.read_csv(file_path)
    csv_info = []

    for columns in sorted(file["engagement rate"], reverse=reverse):
        for column in file[file["engagement rate"] == columns].values.tolist():

            if top >= column[4] >= bottom:
                break

            csv_info.append(copy.deepcopy([column[1], column[2], column[3], column[4]]))

        if columns == 0:
            save_csv_tweet_analytics(csv_info, save_file_name)
            csv_info.clear()
            break

        else:
            continue

        save_csv_tweet_analytics(csv_info, save_file_name)
        csv_info.clear()
        break


def main():
    global driver
    path = "my_analytics.csv"
    if not os.path.exists(base_file_path + path):
        # 毎回自分のアナリティクスから呼び出すのは負荷とか時間とか面倒になるので一度保存されたら削除されない限りここはパスする
        login()
        scroll_pages()
        csv_info = scrape()
        driver.close()
        save_csv_tweet_analytics(csv_info, path)

    sort_engagement_rate(base_file_path + path)

    # 上位30件のツイートから単語出現頻度を求めてみる
    select_range(file_path=base_file_path + path, save_file_name="top_30.csv", reverse=True, bottom=0.1)
    texts = pd.read_csv(base_file_path + "top_30.csv")["テキスト"][:30:].tolist()
    texts = mecab_list(" ".join(texts))
    texts = ranking(texts)
    save_csv("my_tweets_top_30", texts)


if __name__ == "__main__":
    main()
