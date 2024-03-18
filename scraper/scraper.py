from tweety import Twitter
import json
import os
import time
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

wait_time = int(os.getenv("WAIT_TIME", 10))

app = Twitter("session")
auth_token = "3d22d7b834d45574b53ee07a3616c3e15ac2dfe7"
app.load_auth_token(auth_token)

# https://twitter.com/kugiwontmiss/status/1768700911134662696
root_tweet_id = "1768700911134662696"
data_dir = "./data"
media_dir = "./data/media"

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

if not os.path.exists(media_dir):
    os.makedirs(media_dir)

media_data = {}


def get_tweet_comments(tweet_id):
    time.sleep(wait_time)
    tweet_detail = app.tweet_detail(tweet_id)
    tweet = {"id": tweet_detail.id, "text": tweet_detail.text, "author": tweet_detail.author.name, "is_reply": tweet_detail.is_reply, "date": tweet_detail.date.strftime("%Y-%m-%d %H:%M:%S"), "reply_counts": tweet_detail.reply_counts, "retweets_counts": tweet_detail.retweet_counts, "likes_counts": tweet_detail.likes, "bookmark_count": tweet_detail.bookmark_count}
    comment_count = tweet_detail.reply_counts
    comment_get = 0
    comment = []
    comment_cursor = None
    while comment_get < comment_count:
        commentsdata = app.get_tweet_comments(tweet_id, pages=1, get_hidden=True, cursor=comment_cursor, wait_time=10)
        comment_cursor = commentsdata.cursor
        comment_get += len(commentsdata)
        if len(commentsdata) == 0:
            return tweet, comment
        for i in commentsdata:
            if len(i.tweets) > 0:
                this_tweet = i.tweets[0]
                if this_tweet.id in [j["id"] for j in comment]:
                    comment_get = 999999999999
                    break
                temp = {"id": this_tweet.id, "text": this_tweet.text, "author": this_tweet.author.name, "is_reply": this_tweet.is_reply, "date": this_tweet.date.strftime("%Y-%m-%d %H:%M:%S"), "reply_counts": this_tweet.reply_counts, "retweets_counts": this_tweet.retweet_counts, "likes_counts": this_tweet.likes, "bookmark_count": this_tweet.bookmark_count}
                comment.append(temp)
                if this_tweet.media:
                    for media in this_tweet.media:
                        save_media(media, this_tweet.id)
        print("tweet_id:", tweet_id, "comment_get:", comment_get)
    return tweet, comment


def get_queue():
    queue = []
    have_explored = os.listdir(data_dir)
    for i in have_explored:
        data = json.load(open(f"{data_dir}/{i}", "r", encoding="utf-8"))
        comment = data[1]
        for j in comment:
            queue.append(j["id"])
    explored_id = [i.split(".")[0] for i in have_explored]
    queue = [i for i in queue if i not in explored_id]
    return queue


def save_media(media, tweet_id):
    if media.type == "photo":
        media_url = media.media_url_https
        parsed_url = urlparse(media_url)
        extension = os.path.splitext(parsed_url.path)[1]
        filename = os.path.join(media_dir, f"{os.path.basename(media_url)}_{tweet_id}{extension}")
        download_media(media_url, filename)
    elif media.type == "video":
        best_stream = max(media.streams, key=lambda s: s.get("bitrate", 0))
        media_url = best_stream["url"]
        parsed_url = urlparse(media_url)
        extension = os.path.splitext(parsed_url.path)[1]
        filename = os.path.join(media_dir, f"{os.path.basename(media_url)}_{tweet_id}{extension}")
        download_media(media_url, filename)
    elif media.type == "animated_gif":
        if media.streams:
            best_stream = media.streams[0]
            media_url = best_stream["url"]
            parsed_url = urlparse(media_url)
            extension = os.path.splitext(parsed_url.path)[1]
            filename = os.path.join(media_dir, f"{os.path.basename(media_url)}_{tweet_id}{extension}")

            download_media(media_url, filename)
        else:
            print("No streams found for animated GIF.")


def download_media(media_url, filename):
    response = requests.get(media_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {media_url} as {filename}")
    else:
        print(f"Failed to download {media_url}")
    time.sleep(wait_time)


queue = [root_tweet_id]
while len(queue) > 0:
    execute_id = queue.pop(0)
    print("Executing:", execute_id)
    try:
        tweet, comments = get_tweet_comments(execute_id)
    except Exception as e:
        queue.append(execute_id)
        time.sleep(60)
        print("Error:", e)
        continue
    with open(f"{data_dir}/{execute_id}.json", "w", encoding="utf-8") as f:
        json.dump([tweet, comments], f, ensure_ascii=False, indent=4, default=str)
    queue.extend([i["id"] for i in comments])
    print("Done:", execute_id)

for media_url, tweet_ids in media_data.items():
    save_media(media_url, tweet_ids)