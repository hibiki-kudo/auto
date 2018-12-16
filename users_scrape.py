# encoding = utf-8

from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

BASE_URI = "https://twitter.com/{user_name}/followers"

# ウェブドライバーのディレクトリをexecutable_pathのところに設定してください
driver = webdriver.Firefox(executable_path="geckodriver")

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
    for i in range(length):
        driver.execute_script(f"window.scrollTo({i}, document.body.scrollHeight);")
        sleep(1)


def open_page(user_name):
    driver.get(BASE_URI.format(user_name=user_name))
    html = driver.page_source
    return int(BeautifulSoup(html, "html.parser").find("a", attrs={"data-nav": "followers"}).find("span", attrs={
        "class": "ProfileNav-value"})["data-count"])


def scrape_users():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    for user in soup.find_all("div", attrs={"class": "ProfileCard-userFields"}):
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
    df = pd.DataFrame(users, columns=['name', 'profile_message', 'url'])
    df.to_csv("followers_info.csv")


def main():
    user_name = "hibikikkk_9712"
    password = "Kudo9712"
    email = "08062909205"

    scrape_user = "sayaendo26"

    login(user_name=user_name, password=password, email=email)
    length = open_page(scrape_user)
    scroll_pages(length // 9)  # 1あたり6人読み込み
    scrape_users()
    driver.close()
    save_csv()


if __name__ == "__main__":
    main()
