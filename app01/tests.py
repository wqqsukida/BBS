from django.test import TestCase
# Create your tests here.
li = [{'ctime': None, 'commenter_id__username': '艾泽拉斯国家地理', 'id': 1, 'content': '这是最新回复1', 'parent_id': None},
      {'ctime': None, 'commenter_id__username': 'user01', 'id': 2, 'content': '这是最新回复2', 'parent_id': None},
      {'ctime': None, 'commenter_id__username': 'user02', 'id': 3, 'content': '这是最新回复1-1', 'parent_id': 1},
      {'ctime': None, 'commenter_id__username': 'user03', 'id': 4, 'content': '这是最新回复1-2', 'parent_id': 1},
      {'ctime': None, 'commenter_id__username': 'Dylan', 'id': 5, 'content': '这是最新回复1-1-1', 'parent_id': 3},
      {'ctime': None, 'commenter_id__username': 'Elaine', 'id': 6, 'content': '这是最新回复1-1-2', 'parent_id': 3}]


def build_comment_data(li):
    dic = {}
    for item in li:
        item['children'] = []
        dic[item['id']] = item

    result = []
    for item in li:
        pid = item['parent_id']
        if pid:
            dic[pid]['children'].append(item)
        else:
            result.append(item)

    return result

l= build_comment_data(li)
print(l)






l = [{'parent_id': None, 'ctime': None, 'id': 1, 'commenter_id__username': '艾泽拉斯国家地理', 'content': '这是最新回复1', 'children': [
    {'parent_id': 1, 'ctime': None, 'id': 3, 'commenter_id__username': 'user02', 'content': '这是最新回复1-1', 'children': [
        {'parent_id': 3, 'ctime': None, 'id': 5, 'commenter_id__username': 'Dylan', 'content': '这是最新回复1-1-1', 'children': []},
        {'parent_id': 3, 'ctime': None, 'id': 6, 'commenter_id__username': 'Elaine', 'content': '这是最新回复1-1-2', 'children': []}]},
    {'parent_id': 1, 'ctime': None, 'id': 4, 'commenter_id__username': 'user03', 'content': '这是最新回复1-2', 'children': []}]},
     {'parent_id': None, 'ctime': None, 'id': 2, 'commenter_id__username': 'user01', 'content': '这是最新回复2', 'children': []}]






















