from tweety import Twitter
import json
import os
import time

app = Twitter("session")
auth_token = "3d22d7b834d45574b53ee07a3616c3e15ac2dfe7"
app.load_auth_token(auth_token)

# root_tweet_id="1742670392849060162"  #爬取的推文id
root_tweet_id = "1767758341554462915"
fileroute = "./data/second"

def get_tweet_comments(tweet_id):
    tweet_detail = app.tweet_detail(tweet_id)
    tweet = {"id": tweet_detail.id, "text": tweet_detail.text, "author":tweet_detail.author.name ,"is_reply": tweet_detail.is_reply,
             "date": tweet_detail.date.strftime("%Y-%m-%d %H:%M:%S"),  "url": tweet_detail.url, "views_counts": tweet_detail.views, "reply_counts": tweet_detail.reply_counts,
             "retweets_counts": tweet_detail.retweet_counts, "likes_counts": tweet_detail.likes, "bookmark_count": tweet_detail.bookmark_count}
    
    comment_count = tweet_detail.reply_counts #评论的数量
    # print(comment_count)
    comment_get = 0
    comment = []
    comment_cursor = None #评论的游标
    while comment_get < comment_count :
        commentsdata = app.get_tweet_comments(tweet_id, pages = 1, get_hidden = True, cursor = comment_cursor, wait_time = 10)
        comment_cursor = commentsdata.cursor
        comment_get += len(commentsdata)
        if len(commentsdata) == 0:
            return [tweet, comment]
        for i in commentsdata:
            if len(i.tweets) > 0:
                this_tweet = i.tweets[0]
                #如果id出现过，说明已经爬取过了
                if this_tweet.id in [j["id"] for j in comment]:
                    comment_get = 999999999999
                    break
                temp = {"id": this_tweet.id, "text": this_tweet.text, "author": this_tweet.author.name, "is_reply": this_tweet.is_reply,
                        "date": this_tweet.date.strftime("%Y-%m-%d %H:%M:%S"),  "url": this_tweet.url, "views_counts": this_tweet.views, "reply_counts": this_tweet.reply_counts,
                        "retweets_counts": this_tweet.retweet_counts, "likes_counts": this_tweet.likes, "bookmark_count": this_tweet.bookmark_count}
                comment.append(temp)
            
        print("tweet_id:",tweet_id, "comment_get:", comment_get)
    return [tweet, comment]

def get_queue():
    queue = []
    have_explored = os.listdir(fileroute)
    for i in have_explored:
        data = json.load(open(f"{fileroute}/{i}", "r", encoding="utf-8"))
        comment = data[1]
        for j in comment:
            queue.append(j["id"])
    #去掉explorer过的, have_explore里面文件的name是id.json
    explored_id = [i.split(".")[0] for i in have_explored]
    queue = [i for i in queue if i not in explored_id]
    return queue
    
# queue = get_queue()
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
    with open (f"{fileroute}/{execute_id}.json", "w", encoding="utf-8") as f:
        json.dump( [tweet, comments], f, ensure_ascii=False, indent=4)
    queue.extend([i["id"] for i in comments])
    print("Done:", execute_id)
