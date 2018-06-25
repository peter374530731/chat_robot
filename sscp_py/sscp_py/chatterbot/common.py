# import pymysql
# import contextlib
from . import handlemsg
import logging
import re
logger = logging.getLogger('django')



#定义上下文管理器，连接后自动关闭连接
'''
@contextlib.contextmanager
def mysql(host='10.75.2.121', port=3306, user='root', passwd='SunLand2@', db='sunlands',charset='utf8'):
  conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
  cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
  try:
    yield cursor
  finally:
    conn.commit()
    cursor.close()
    conn.close()
'''

#去除数组中最大三个值的下标
'''
def find3max(arr):
    m1, m2, m3 = -1, -1, -1
    i1, i2, i3 = -1, -1, -1
    for i in range(0, len(arr)):
        if (arr[i] == 0):
            continue
        if (arr[i] > m1):
            m3 = m2
            i3 = i2
            m2 = m1
            i2 = i1
            m1 = arr[i]
            i1 = i
        elif (arr[i] > m2):
            m3 = m2
            i3 = i2
            m2 = arr[i]
            i2 = i
        elif (arr[i] > m3):
            m3 = arr[i]
            i3 = i
    return i1, i2, i3
'''

def allindict(segs, dt):
    try:
        for seg in segs:
            if seg not in dt:
                return False
        return True
    except Exception as e:
        logger.error("ERROR:%s" % str(e))


def getCategory2(content):
    # logger.info('getCategory :%s' % content)
    try:
        try:
            content = content.lower()
        except Exception as ex:
            print("getCategory2 trance to lower error: %s" % str(ex))

        if 'http' in content:
            return '链接'
        content = handlemsg.HandleMsg.onlycutMsg(content)
        if content == [] or content == [''] or len(content) == 0:
            return '无效会话'

        stopwords = ['的','了', '呢', '吗', '吧', '嗯', '恩', '哦','哒','呐','额','啊',
                            '呀','滴','哟','么','哈','～','嘛','咧','嘞','呃',' ',
                     'good','嗨','帮助','太','劳','劳你','劳您','实在','you','让']

        content_copy = []
        for content_item in content:
            if content_item in stopwords:
                continue
            else:
                content_copy.append(content_item)

        del stopwords

        if len(content_copy)==0:
            return '无效会话'

        pp = ['老师', '班主任', '主任', '班任', '你', '您', '班班', '亲', '亲爱', '亲爱的']

        content_copy_2 = []
        for content_item in content_copy:
            if content_item in pp:
                continue
            else:
                content_copy_2.append(content_item)

        del pp

        segs = []
        for seg in content_copy_2:
            if(seg!=' ' and seg!='' and seg!=[]):
                segs.append(seg)

        #预处理规则
        preProcRules = [[['在', '有人', '在哪', '在吗', '在么', '在在', '哈喽', '在不', '在没', '没在', '在听',
                          '老师好', '班主任好', '主任好', '班任好', '班班好', '早', '早上好', '早啊', '早安',
                          '午安', '晚安', '有人没', '有人在', '早上好','上午好', '下午好', '中午好', '下班',
                          '晚上好', '在不在', '人', '可在', '上班', '有空', '你好', '您好', '下班', 'hi',
                          'morning', 'afternoon', 'noon','enenging'], '问候'],
                        [['谢', '谢谢', '好谢谢', '多谢', '感谢你', '感谢您', '感谢', '谢谢您', '谢谢你', '非常感谢',
                          '劳驾', 'thank', '费心', '3q', '过意不去', '辛苦', '拜托', '麻烦'], '感谢'],
                        [['好'],'结束语']]

        for rule in preProcRules:
            if (allindict(segs, rule[0])):
                return rule[1]

        del preProcRules

        return ''

    except Exception as e:
        print("getCategory ERROR: %s" % str(e))
        return ''


def getCategory(content):
    return_dict = {'category': '', 'content': ''}

    try:
        content = content.lower()
    except Exception as ex:
        print("getCategory trance to lower error: %s" % str(ex))

    re_config = re.compile(r'[^(\u4e00-\u9fa5)|(a-z)|(A-Z)|(0-9)]')
    get_list = re_config.split(content)
    split_list=[]

    for get_item in get_list:
        if len(get_item)>0:
            split_list.append(get_item)

    if len(split_list) >= 3:
        _msg = ''.join([split_list[0], split_list[1]])
        first_category = getCategory2(_msg)

        if first_category == '':
            second_category = getCategory2(split_list[0])
            if second_category == '':
                return_dict['content'] = content
                return return_dict
            else:
                return_dict['category'] = second_category
                return_str = ''
                for i in range(1, len(split_list)):
                    return_str = return_str + " " + split_list[i]
                return_dict['content'] = return_str
                return return_dict
        else:
            return_dict['category'] = first_category
            return_str = ''
            for i in range(2,len(split_list)):
                return_str = return_str + " " + split_list[i]
            return_dict['content'] = return_str
            return return_dict

    elif len(split_list) ==2:
        _msg = ''.join([split_list[0], split_list[1]])
        first_category = getCategory2(_msg)
        if first_category == '':
            second_category = getCategory2(split_list[0])
            if second_category == '':
                return_dict['content'] = content
                return return_dict
            else:
                return_dict['content'] = split_list[1]
                return return_dict
        else:
            return_dict['category'] = first_category
            return return_dict


    else:
        get_msg = getCategory2(content)
        if get_msg == '':
            return_dict['content'] = content
            return return_dict
        else:
            return_dict['category'] = get_msg
            return return_dict

'''
def getWordName(word, index):
    if (index >= 0):
        return word[index]
    else:
        return ''


def getCategoryFitNames(labels, countArray, word, n_clusters):
    fitNames = [''] * n_clusters
    label_count_array = [[0] * len(word)] * n_clusters
    for i in range(0, len(countArray)):
        label_count_array[labels[i]] += countArray[i]

    for i in range(0, n_clusters):
        i1, i2, i3 = find3max(label_count_array[i])
        fitNames[i] = '%s %s %s' % (getWordName(word, i1), getWordName(word, i2), getWordName(word, i3))
    return fitNames


def count_labels(labels):
    count = 0
    dt = set([])
    for l in labels:
        if (l not in dt):
            count = count + 1
            dt.add(l)
    return count
'''

def test():
    print(getCategory('老师下午好'))

if __name__ == '__main__':
    test()