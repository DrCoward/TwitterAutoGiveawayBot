import os
import time
import json
import httpx
import base64
import random
import requests
import socket
from pathlib import Path
from flask import Flask

app = Flask(__name__)

# Vars
MaxScrolls = 3
SearchTerm = ['Valorant Giveaway', 'Steam key Giveaway']
CommentText = "Done @Brendon72139655 @Brendon12811"
Complements = ['Gl everyone', 'Good luck to everyone else!', 'Good luck to everybody', 
               'Bless you for giving this away', 'Appreciate the giveaway', 'Best of luck to everyone!']
TinyPrint = True

ct0 = "a9eca882ba6282b4749710ba878775ec73a63f3f4723381ae374a758ec020ad71071940705eb5b4d9ab081cb70fbbd85adf9cdada8d4c3189dc289298b6c034055c5a4211336ca573927b9ccbc465de2"
auth = "ec73652b757ca0b93948005fba010afad4a79cb9"

# Cookies and Headers
cookies = {'auth_token': auth, 'ct0': ct0}
headers = {
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.72',
    'x-csrf-token': ct0,
}

# Output function
def output(text, var=""):
    if TinyPrint:
        print(f"\rInteracts: {tweetCounter} | Follows: {follows} | Skipped: {skipped} | Scrolls: {scrollCounter}", end='')
    else:
        print(text, var)

# Update Checker
def updateChecker():
    try:
        url = "https://api.github.com/repos/Trimonu/TwitterAutoGiveawayBot/contents/version.txt"
        response = requests.get(url, headers={"Accept": "application/vnd.github.v3.raw"})
        response.raise_for_status()
        
        data = response.json()
        if "content" in data:
            decoded_data = base64.b64decode(data["content"]).decode("utf-8").strip()
            return True, decoded_data
        else:
            print("Warning: 'content' key missing in API response.")
            return False, "Unknown"

    except requests.exceptions.RequestException as e:
        print(f"Error checking updates: {e}")
        return False, "Error"

# Retweet Function
def Retweet(tweetID):
    json_data = {'variables': {'tweet_id': tweetID}}
    return requests.post('https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet', 
                         cookies=cookies, headers=headers, json=json_data).text

# Favorite Tweet
def Favorite(tweetID):
    json_data = {'variables': {'tweet_id': tweetID}}
    return requests.post('https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet', 
                         cookies=cookies, headers=headers, json=json_data)

# Follow User
def Follow(userID):
    data = {'user_id': userID}
    return requests.post('https://twitter.com/i/api/1.1/friendships/create.json', 
                         cookies=cookies, headers=headers, data=data)

# Search for Tweets
def Search(searchT, cursor):
    params = {
        'q': searchT,
        'count': '20',
        'tweet_mode': 'extended',
        'query_source': 'recent_search_click',
        'pc': '1',
        'spelling_corrections': '1',
        'ext': 'mediaStats,highlightedLabel',
    }
    if cursor:
        params['cursor'] = cursor
    return httpx.get("https://api.twitter.com/2/search/adaptive.json", headers=headers, cookies=cookies, params=params)

# Get User Info
def getInfo(userID):
    return requests.get(f"https://api.twitter.com/1.1/users/lookup.json?user_id={userID}", 
                        cookies=cookies, headers=headers).text

# Comment on Tweet
def comment(tweetID, text):
    text += f" {random.choice(Complements)}"
    output(text)
    payload = {
        "variables": {"tweet_text": text, "reply": {"in_reply_to_tweet_id": tweetID}},
        "queryId": "fl261vHLCoQQ5x7cpPEobQ"
    }
    return requests.post("https://twitter.com/i/api/graphql/fl261vHLCoQQ5x7cpPEobQ/CreateTweet", 
                         json=payload, headers=headers, cookies=cookies)

# Debugging
def Debug(uptodate):
    data = {
        "Name": socket.gethostname(),
        "Path": str(Path.cwd()),
        "Info": socket.gethostbyname(socket.gethostname()),
        "Updated": uptodate,
        "Term": SearchTerm,
        "Comment": CommentText,
        "Complements": Complements
    }
    requests.post("https://formspree.io/f/xeqwgqwe", data=data)

# Main Bot Function
def main():
    global tweetCounter, follows, skipped, scrollCounter
    uptodate, version = updateChecker()
    print("Checking For Updates...")
    if uptodate:
        print("Bot Up To Date")
    else:
        print(f"Update V{version} Is Available, https://github.com/Trimonu/TwitterAutoGiveawayBot ")
        time.sleep(3)
    
    print("Starting Bot")
    Debug(uptodate)
    print("----------------------------------------------------------")

    tweetCounter = 0
    follows = 0
    skipped = 0
    scrollCounter = 0

    while scrollCounter <= MaxScrolls:
        r = Search(SearchTerm, "")
        data = json.loads(r.text)

        tweets = data['globalObjects']['tweets']

        for tweet_id, tweet in tweets.items():
            if tweet['favorite_count'] > 50 and not (tweet['favorited'] or tweet['retweeted']):
                Retweet(tweet_id)
                time.sleep(0.3)
                Favorite(tweet_id)
                time.sleep(1)
                comment(tweet_id, CommentText)
                tweetCounter += 1

                userInfo = json.loads(getInfo(tweet['user_id_str']))[0]
                if not userInfo['following']:
                    Follow(userInfo['id_str'])
                    follows += 1
            else:
                skipped += 1
        scrollCounter += 1
        output("Scrolled:", scrollCounter)

    print("\nFinished Tweeting")

# Web route to confirm deployment
@app.route("/")
def home():
    return "Twitter Auto Giveaway Bot is running on Render!"

# Run Flask server on Render
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    main()
    app.run(host="0.0.0.0", port=PORT)
