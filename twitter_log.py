#!/usr/bin/env python3.6
import datetime
import json
import os

import tweepy


def open_file(fname, *args, **kwargs):
    cwd = os.path.dirname(__file__)
    fname = os.path.join(cwd, fname)
    return open(fname, *args, **kwargs)


def write_items(fp, title, items):
    fp.write('{}\n'.format(title))
    for key, value in items.items():
        if value:
            fp.write('{key} {value[name]} {value[screen_name]}\n'.format(
                key=key, value=value))
        else:
            fp.write('{key}\n'.format(key=key))


def diff(old, new):
    added, removed = [], []
    for item in set(old) | set(new):
        if item not in old:
            added.append(item)
        elif item not in new:
            removed.append(item)

    return added, removed


def get_user(api, id_str):
    user = api.get_user(id_str)
    return {
        'name': user.name,
        'screen_name': user.screen_name,
    }


def first_run(api):
    followers = {
        user.id_str: {
            'name': user.name,
            'screen_name': user.screen_name,
        }

        for user in list(tweepy.Cursor(api.followers).items())
    }
    friends = {
        user.id_str: {
            'name': user.name,
            'screen_name': user.screen_name,
        }

        for user in list(tweepy.Cursor(api.friends).items())
    }

    with open_file('followers.json', 'w') as fp:
        json.dump(followers, fp, indent=2)

    with open_file('friends.json', 'w') as fp:
        json.dump(friends, fp, indent=2)


CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('TWITTER_ACCESS_KEY')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%z')

if __name__ == '__main__':
    followers_ids = list(map(str, api.followers_ids()))
    friends_ids = list(map(str, api.friends_ids()))

    # Load old
    try:
        with open_file('followers.json', 'r') as fp:
            old_followers = json.load(fp)
    except:
        old_followers = {}

    try:
        with open_file('friends.json', 'r') as fp:
            old_friends = json.load(fp)
    except:
        old_friends = {}

    old_followers_ids = old_followers.keys()
    old_friends_ids = old_friends.keys()

    new_followers_ids, unfollowers_ids = diff(old_followers_ids, followers_ids)
    new_friends_ids, unfriends_ids = diff(old_friends_ids, friends_ids)

    new_followers = {
        id_str: get_user(api, id_str)
        for id_str in new_followers_ids
    }

    unfollowers = {
        id_str: old_followers[id_str]
        for id_str in unfollowers_ids
    }

    new_friends = {
        id_str: get_user(api, id_str)
        for id_str in new_friends_ids
    }

    unfriends = {
        id_str: old_friends[id_str]
        for id_str in unfriends_ids
    }

    if any((new_followers, unfollowers, new_friends, unfriends)):
        with open_file(f'log_{timestamp}', 'w') as fp:
            write_items(fp, 'New followers:', new_followers)
            write_items(fp, 'Unfollowers:', unfollowers)
            write_items(fp, 'New friends:', new_friends)
            write_items(fp, 'Unfriends', unfriends)

    # Write new
    with open_file('followers.json', 'w') as fp:
        followers = {
            id_str: old_followers[id_str]
            for id_str in old_followers_ids
            if id_str not in unfollowers_ids
        }
        followers.update(new_followers)
        json.dump(followers, fp, indent=2)

    with open_file('friends.json', 'w') as fp:
        friends = {
            id_str: old_friends[id_str]
            for id_str in old_friends_ids
            if id_str not in unfriends_ids
        }
        friends.update(new_friends)
        json.dump(friends, fp, indent=2)
