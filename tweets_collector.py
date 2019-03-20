import tweepy
from pymongo import MongoClient, DESCENDING
from tweepy import OAuthHandler
from pprint import pprint
import matplotlib.pyplot as plt   
import time

# connect to mongo
client = MongoClient('localhost', 27017)
db = client.FakeNews

def get_followers_of_user(api, name, user_id, users_per_page=5000):
    page = 1
    tweets = api.followers_ids(id=user_id, page=page, count=users_per_page)
    print len(tweets['ids'])
    print tweets['ids']

    while len(tweets) > 0:
        page = page + 1
        print 'page++'
        tweets = api.followers_ids(id=user_id, page=page, count=users_per_page)
        print len(tweets['ids'])
        print tweets['ids']


def collect_tweets_of_user(api, name, user_id, tweets_per_page=200):
    page = 1
    tweets = api.user_timeline(id=user_id, page=page, count=tweets_per_page)
    for tweet in tweets:
        db[name].insert_one(tweet)
    while len(tweets) > 0:
        page = page + 1
        tweets = api.user_timeline(id=user_id, page=page, count=tweets_per_page)
        for tweet in tweets:
            db[name].insert_one(tweet)


def collect_retweets_of_a_tweet(api, initial_id, name, tweets_per_page=100):
    page = 1
    retweets = api.retweets(id=initial_id, page=page, count=tweets_per_page)
    for tweet in retweets:
        db[name+'_retweets'].insert_one(tweet)
    while len(retweets) > 0:
        page = page + 1
        retweets = api.retweets(id=initial_id, page=page, count=tweets_per_page)
        for tweet in retweets:
            db[name + '_retweets'].insert_one(tweet)


def collect_initial_tweets(api):
    #collect_tweets_of_user(api, 'Fake', '735574058167734273')
    collect_tweets_of_user(api, 'Real', '5402612')


def get_top_k(collection_name, field_name, limit):
    return db[collection_name].find().sort([[field_name, DESCENDING]]).limit(limit)


def get_retweets_of_tweet(collection_name, id, limit = 180):
    if limit == 0:
        return db[collection_name].find({'retweeted_status.id_str': id})
    else:
        return db[collection_name].find({'retweeted_status.id_str': id}).limit(limit)


def check_friendship(api, userA, userB):
    try:
        return api.show_friendship(source_id=userA, target_id=userB)
    except tweepy.TweepError:
        print("Failed to run the command on that user, Skipping...")
        return 'none'

def get_users_who_retweeted(collection_name, id):
    ids = []
    for tweet in get_retweets_of_tweet(collection_name, id):
        ids.append(tweet['user']['id'])
    return ids

#theo part
def find_user_per_hop(initial_user_id, users_that_retweeted):
    friendships = []
    users_no_relation_after_step_1 = []
    first_hop = []
    hop1=0
    hop2=0
    hop3=0
    hop4=0
    hop5=0

   
    print '1ST HOP'

    for user in users_that_retweeted:
        #print user
        friendship = check_friendship(api, initial_user_id, user)
        if friendship == 'none':
            continue
        following = friendship['relationship']['source']['following']
        followed = friendship['relationship']['source']['followed_by']
        if followed or following:
            print 'FRIENDS!'
            hop1+=1
            friendships.append((initial_user_id, user))
            first_hop.append(user)
        else:
            print 'NO FRIENDS'
            users_no_relation_after_step_1.append(user)

    second_hop = []
    users_no_relation_after_step_2 = []
    

    print '2ND HOP'

    for user in users_no_relation_after_step_1:
        found = False
        #print user
        for source_user in first_hop:
            friendship = check_friendship(api, source_user, user)
            following = friendship['relationship']['source']['following']
            followed = friendship['relationship']['source']['followed_by']
            if followed or following:
                found = True
                print 'FRIENDS!'
                hop2+=1
                friendships.append((source_user, user))
                second_hop.append(user)
                break
            else:
                print 'NO FRIENDS'
        if not found:
            users_no_relation_after_step_2.append(user)

    third_hop = []
    users_no_relation_after_step_3 = []

    print '3RD HOP'

    for user in users_no_relation_after_step_2:
        found = False
        #print user
        for source_user in second_hop:
            friendship = check_friendship(api, source_user, user)
            following = friendship['relationship']['source']['following']
            followed = friendship['relationship']['source']['followed_by']
            if followed or following:
                found = True
                print 'FRIENDS!'
                hop3+=1
                friendships.append((source_user, user))
                third_hop.append(user)
                break
            else:
                print 'NO FRIENDS'
            if not found:
                users_no_relation_after_step_3.append(user)

    fourth_hop = []
    users_no_relation_after_step_4 = []

    print '4TH HOP'

    for user in users_no_relation_after_step_3:
        found = False
        #print user
        for source_user in third_hop:
            friendship = check_friendship(api, source_user, user)
            following = friendship['relationship']['source']['following']
            followed = friendship['relationship']['source']['followed_by']
            if followed or following:
                found = True
                print 'FRIENDS!'
                hop4+=1
                friendships.append((source_user, user))
                fourth_hop.append(user)
                break
            else:
                print 'NO FRIENDS'
            if not found:
                users_no_relation_after_step_4.append(user)

    fifth_hop = []
    users_no_relation_after_step_5 = []

    print '5TH HOP'

    for user in users_no_relation_after_step_4:
        found = False
        #print user
        for source_user in fourth_hop:
            friendship = check_friendship(api, source_user, user)
            following = friendship['relationship']['source']['following']
            followed = friendship['relationship']['source']['followed_by']
            if followed or following:
                found = True
                print 'FRIENDS!'
                hop5+=1
                friendships.append((source_user, user))
                fifth_hop.append(user)
                break
            else:
                print 'NO FRIENDS'
            if not found:
                users_no_relation_after_step_5.append(user) 
    
    return friendships, first_hop, second_hop, third_hop, fourth_hop, fifth_hop, hop1, hop2, hop3, hop4, hop5



if __name__ == '__main__':
    
    # private keys: create an app on apps.twitter.com
    consumer_key = 'FkXH9u9z4erMLKVXCSBN8NQIB'
    consumer_secret = 'kbvQVKi6qYfnmx87vKNroCJxJ84x9h8KGRVp3A1cSborZ3ft87'
    access_token = '978456990-19gBiHo7yciV0Fqfh2OKQ7MF5tISqxYOebC6BhCZ'
    access_secret = 'mXW4LhnV85x5bsqfPUyCOhsnZf8iRYmxllOQG5dg6NwCu'

    # connecting to twitter
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     parser=tweepy.parsers.JSONParser())

    # COLLECTING INITIAL TWEETS
'''
    collect_initial_tweets(api)

    top3RealTweets = get_top_k('Real', 'retweet_count', 3)
    top3FalseTweets = get_top_k('Fake', 'retweet_count', 3)
    
    # COLLECTING RETWEETS

    for tweet in top3RealTweets:
       print tweet
       collect_retweets_of_a_tweet(api, tweet['id_str'], 'Real')

    for tweet in top3FalseTweets:
        print tweet
        collect_retweets_of_a_tweet(api, tweet['id_str'], 'Fake')
'''
#get_followers_of_user(api, 'test', '5402612')
    


