from bilibili_api import search, sync


if __name__ == '__main__':
    content = sync(search.search("刀剑神域",page=0))
    print(content)