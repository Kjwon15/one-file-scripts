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
    added, removed = {}, {}
    for key in set(old.keys()) | set(new.keys()):
        if key not in old:
            added[key] = new[key]
        elif key not in new:
            removed[key] = old[key]

    return added, removed


def get_users(method):
    return {
        user.id_str: {
            'name': user.name,
            'screen_name': user.screen_name,
        }
        for user in tweepy.Cursor(method).items()
    }


CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_KEY = os.getenv('TWITTER_ACCESS_KEY')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S_%z')

if __name__ == '__main__':
    followers = get_users(api.followers)
    friends = get_users(api.friends)

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

    new_followers, unfollowers = diff(old_followers, followers)
    new_friends, unfriends = diff(old_friends, friends)

    if any((new_followers, unfollowers, new_friends, unfriends)):
        with open_file(f'log_{timestamp}', 'w') as fp:
            write_items(fp, 'New followers:', new_followers)
            write_items(fp, 'Unfollowers:', unfollowers)
            write_items(fp, 'New friends:', new_friends)
            write_items(fp, 'Unfriends', unfriends)

    # Write new
    with open_file('followers.json', 'w') as fp:
        json.dump(followers, fp, indent=2)

    with open_file('friends.json', 'w') as fp:
        json.dump(friends, fp, indent=2)
