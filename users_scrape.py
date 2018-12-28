# encoding = utf-8

from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from morphological_analysis import analysis

BASE_URI = "https://twitter.com/{user_name}/followers"

# ウェブドライバーのディレクトリをexecutable_pathのところに設定してください
driver = webdriver.Firefox(executable_path="./geckodriver")

users = []


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


def scroll_pages(length):
    try:
        for i in range(length):
            before_html = driver.page_source
            driver.execute_script(f"window.scrollTo({i+1}, document.body.scrollHeight);")
            sleep(2)

            if len(before_html) == len(driver.page_source):
                print(len(before_html))
                print(len(driver.page_source))
                break

    except:
        scrape_users()
        driver.close()
        save_csv()


def open_page(user_name):
    driver.get(BASE_URI.format(user_name=user_name))
    html = driver.page_source
    return int(BeautifulSoup(html, "html.parser").find("a", attrs={"data-nav": "followers"}).find("span", attrs={
        "class": "ProfileNav-value"})["data-count"])


def scrape_users():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    for user in soup.find_all("div", attrs={"class": "ProfileCard-userFields"}):
        '''
        コメントアウトしている部分はrequestsモジュールで完全なプロフィール欄を抜き取ることができる。
        ただこっちはユーザ毎にリクエストを出すため、サーバに掛かる負荷が大きい。そのため、小休止を毎回入れるとすごい時間がかかるためおすすめはしない。
        '''
        # sleep(2)
        # profile = requests.get(f"https://twitter.com/" + user.find("b", attrs={"class": "u-linkComplex-target"}).text.replace("\n",'').replace("Follows you", "").replace(" ", "") + "/")
        # profile_text = BeautifulSoup(profile.text,"html.parser").find("p",attrs={"class":"ProfileHeaderCard-bio u-dir"}).text
        # users.append([user.find("div", attrs={"class": "ProfileNameTruncated account-group"}).text.replace("\n", "").replace(" ",""),
        #               profile_text,
        #               profile.url])
        # print("@"+user.find("div", attrs={"class": "ProfileNameTruncated account-group"}).text.replace("\n", "").replace(" ",""))
        # print(profile_text)
        # print(profile.url)

        user_name = user.find("div", attrs={"class": "ProfileNameTruncated account-group"}).text.replace("\n",
                                                                                                         "").replace(
            " ", "")

        profile_url = f"https://twitter.com/" + user.find("b", attrs={"class": "u-linkComplex-target"}).text.replace(
            "\n", '').replace("Follows you", "").replace(" ", "") + "/"

        profile_text = user.find("p", attrs={"class": "ProfileCard-bio u-dir"}).text

        users.append([user_name,
                      profile_text,
                      profile_url])

        print("@" + user_name)
        print(profile_text)
        print(profile_url)


def save_csv():
    global scrape_user
    df = pd.DataFrame(users, columns=['name', 'profile_message', 'url'])
    df.to_csv(f"./csvファイル/{scrape_user}_followers_info.csv")


def finish_process():
    scrape_users()
    driver.close()
    save_csv()


def main():
    global scrape_user
    # ログインしないとユーザのフォロワ見れないのでログイン用
    user_name = ""
    password = ""
    email = ""

    # 抜き取るユーザのnameを入力
    scrape_user = ""

    login(user_name=user_name, password=password, email=email)
    length = open_page(scrape_user)  # 今は全フォロワーを取得するよう設定中
    # length = 100  # ここの数字を変えてコードに加えることで人数調整可能
    scroll_pages(length // 10)  # フォロワー1人あたり6人読み込みだけど10で割ったほうがちょうど良さげ
    finish_process()
    analysis(scrape_user)


if __name__ == "__main__":
    main()
