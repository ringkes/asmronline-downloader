def sort_result(result):
    """
    对作品列表排序：
    先按 release 时间倒序（最新在前），再按 name 升序，最后按 aname 升序。
    :param result: 作品字典列表
    :return: 排序后的新列表
    """
    return sorted(result, key=lambda x: (
        -int(x["release"].replace('-', '') or 0),
        x["name"],
        x["aname"]
    ))

def print_works(result):
    """
    美观打印作品主要字段，按指定排序。
    :param result: 作品字典列表
    """
    for item in sort_result(result):
        print(f"index: {item['index']} | title: {item['title']} | work_id: {item['work_id']} | aname: {item['aname']} | tags: {item['tags']} | release: {item['release']}") 