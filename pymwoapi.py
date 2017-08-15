#!/usr/bin/env python

import requests

def _fetch_json(url):
    response = requests.get(url)
    data = response.json()
    if not response.ok:
        # unfortunaley does pgi use both 'error' and 'message' to deliver
        # error messages
        if 'error' in data:
            message = "Error {0}: {1}".format(data['status'], data['error'])
        elif 'message' in data:
            message = "Error {0}: {1}".format(data['status'], data['message'])
        else:
            message = "Unknown Error"
        raise RuntimeError(message)
    return data

def _fetch_game_json(key, id):
    url = "https://mwomercs.com/api/v1/matches/{0}?api_token={1}".format(id, key)
    return _fetch_json(url)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose mode", action="store_true")
    parser.add_argument("key", help="Secret Key. Get it from https://mwomercs.com/profile/api", 
            type=str)
    parser.add_argument("id", help="game-ids as displayed", type=str, nargs="+")
    # parse args
    args = parser.parse_args()

    for gid in args.id:
        print _fetch_game_json(args.key, gid)
