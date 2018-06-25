import re


class RE(object):

    @classmethod
    def re_repear(cls,string):
        pattern=''
        re.match(pattern, string, flags=0)
        re.search(pattern, string, flags=0)


        #pattern : 正则中的模式字符串。
        #repl : 替换的字符串，也可为一个函数。
        #string : 要被查找替换的原始字符串。
        #count : 模式匹配后替换的最大次数，默认 0 表示替换所有的匹配。
        repl=''
        re.sub(pattern, repl, string, count=0, flags=0)
        return