import json
from bilibili_api import homepage, sync


def main():
    top_videos=sync(homepage.get_videos())
    print(f"1:{top_videos.keys()}")
    # print(f"{top_videos['floor_info']}")
    # print(f"{len(top_videos['item'])}")
    print(f"item[1]:{top_videos['item'][0].keys()}")
    print(f"item[1]:{top_videos['item'][0]}")
if __name__ == '__main__':
    main()