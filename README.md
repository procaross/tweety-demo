# Twitter Comment & Media Crawler

该工具用于下载给定Twitter推文的评论和媒体内容(图片、视频和GIF)。它可以从指定的起始推文逐层遍历并下载所有相关评论以及评论中包含的媒体内容。下载的数据将以JSON格式保存，媒体文件将保存在指定的目录中。

## 使用方法

1. 安装所需的Python库:

```
pip install -r requirements.txt
```

2. 从Twitter获取账号认证令牌，并参考`.env.example`在项目根目录创建一个`.env`文件，
将认证令牌保存为`AUTH_TOKEN`变量。还可以在此处设置请求之间的等待时间(`WAIT_TIME`，以秒为单位)，以及起始推文ID(`ROOT_TWEET`，必填项)。

```
AUTH_TOKEN=your_auth_token_here
WAIT_TIME=10
ROOT_TWEET=root_tweet_id
```

> 关于获取AUTH_TOKEN，可参考[这篇教程](https://goodcoin.medium.com/%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E6%8E%A8%E7%89%B9-twitter-%E8%B4%A6%E5%8F%B7%E7%9A%84token%E5%AE%9E%E7%8E%B0token%E4%B8%80%E9%94%AE%E7%99%BB%E5%BD%95-d9f5b21f60da)

3. 运行`scraper.py`脚本。下载的数据将保存在`data`目录下，媒体文件将保存在`data/media`目录下。

```
python3 scraper/scraper.py
```

## 宇宙安全声明

- 请确保您拥有下载推文内容的合法权限，并遵守Twitter的服务条款和隐私政策。
- 该工具使用Twitter的官方API进行数据获取，请合理控制请求频率，避免被封禁。
- 由于Twitter API的限制，该工具可能无法下载所有评论和媒体内容。
- 该工具仅用于个人学习和研究目的，请勿将其用于任何违法或不当用途。
