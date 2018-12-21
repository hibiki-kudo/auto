import copy

import pandas as pd

from search import TwitterSearch

if __name__ == "__main__":
    query = "taka8rie"  # 抜き取るユーザーネーム

    twitter = TwitterSearch()
    twitter.search(f"from:{query}")

    csv_info = []
    while True:
        try:
            for tweet in twitter.tweets:
                csv_info.append([copy.deepcopy(tweet.user), copy.deepcopy(tweet.fullname), copy.deepcopy(tweet.text),
                                 copy.deepcopy(tweet.timestamp)])

            twitter.scroll()

            if len(csv_info) >= 1000:
                break

        except:
            print("収集終了")
            break

    df = pd.DataFrame(csv_info, columns=["screen_name", "name", "text", "timestamp"])  # 取得情報は
    df.to_csv(f"{query}'s_tweet_info.csv")  # 保存するcsvファイル名
