#!/usr/bin/python
# -*- coding: utf-8 -*-
import jieba
import re
from sscp_py.models import AiFilterRule,AiWord,AiSynonym
import logging

logger = logging.getLogger('django')

class HandleMsg(object):
    # 全局变量，存储过滤规则信息
    logger.info("chatterbot.handlemsg.HandleMsg:start class")
    replace_FilterRule_list = []    # 替换规则
    delete_FilterRule_list = []     # 删除规则
    userdict = []                   # 专业词
    addtouser_list = []             # 需要当做专业词使用，但不添加在专业词中的词
    stopwords_dict = {}             # 停止词

    filter_list = []                # 过滤词，需要添加到专业词中
    filter_dict = {}                # 过滤词
    synonym_base_dict = {}          # 基准同义词
    synonym_comon_dict = {}         # 普通同义词

    _local_jieba = jieba            #onlycutMsg方法使用的jieba实例

    # 数据库中获取过滤规则信息
    @classmethod
    def new_FilterRule(cls):
        logger.info("DbAbdHandle.HandleMsg.new_FilterRule:start new_FilterRule")
        # 替换规则
        cls.replace_FilterRule_list = []
        mysql_replace_list = AiFilterRule.objects.filter(type=2)
        for mysql_replace in mysql_replace_list:
            add_array = []
            add_array = [str(mysql_replace.rule), str(mysql_replace.replace_val)]
            cls.replace_FilterRule_list.append(add_array)
        logger.info("replace_FilterRule_list:%s" % str(cls.replace_FilterRule_list))

        # 删除规则
        cls.delete_FilterRule_list = []
        mysql_delete_list = AiFilterRule.objects.filter(type=1)
        for mysql_delete in mysql_delete_list:
            add_array = []
            add_array = [str(mysql_delete.rule), str(mysql_delete.replace_val)]
            cls.delete_FilterRule_list.append(add_array)
        logger.info("delete_FilterRule_list:%s" % str(cls.delete_FilterRule_list))


        add_to_userdict = []
        # 停止词
        cls.stopwords_dict = {}
        # 需要使用fromkeys转为字典形式，所以使用stopwords_list作为临时变量
        stopwords_list = []
        mysql_stopwords_list = AiWord.objects.filter(type=2)
        for mysql_stopwords in mysql_stopwords_list:
            stopwords_list.append(str(mysql_stopwords.word))
            if len(mysql_stopwords.word)>1:
                add_to_userdict.append(mysql_stopwords.word)
        cls.stopwords_dict = {}.fromkeys(stopwords_list)


        #过滤词
        cls.filter_dict = {}
        # 需要使用fromkeys转为字典形式，所以使用stopwords_list作为临时变量
        cls.filter_list = []
        mysql_filter_list = AiWord.objects.filter(type=3)
        for mysql_filter in mysql_filter_list:
            cls.filter_list.append(str(mysql_filter.word))
            if len(mysql_filter.word)>1:
                add_to_userdict.append(mysql_filter.word)
        cls.filter_dict = {}.fromkeys(cls.filter_list)



        # 专业词
        cls.userdict = []
        mysql_userdict_list = AiWord.objects.filter(type=1)
        for mysql_userdict in mysql_userdict_list:
            cls.userdict.append(str(mysql_userdict.word))
        for add_userdict in add_to_userdict:
            cls.addtouser_list.append(add_userdict)


        #同义词
        mysql_Synonym_list = AiSynonym.objects.all()
        for mysql_Synonym in mysql_Synonym_list:
            try:
                if mysql_Synonym.type == 0:
                    cls.synonym_base_dict[mysql_Synonym.synonym_id] = mysql_Synonym.word
                elif mysql_Synonym.type == 1:
                    cls.synonym_comon_dict[mysql_Synonym.word] = mysql_Synonym.parent_id
                if len(mysql_Synonym.word)>1:
                    cls.userdict.append(str(mysql_Synonym.word))
            except Exception as e:
                logger.error('new_FilterRule AiSynonym error %s' % str(e))


        logger.info("stopwords_dict:%s" % str(cls.stopwords_dict))
        logger.info("filter_dict:%s" % str(cls.filter_dict))
        logger.info("userdict:%s" % str(cls.userdict))
        logger.info('synonym_base_dict:%s' % str(cls.synonym_base_dict))
        logger.info('synonym_comon_dict:%s' % str(cls.synonym_comon_dict))


        #更新完数据以后直接添加jieba分词的专业词
        for w in cls.userdict:
            jieba.add_word(w)
            cls._local_jieba.add_word(w)

        for w in cls.addtouser_list:
            jieba.add_word(w)
            cls._local_jieba.add_word(w)

        for f in cls.filter_list:
            jieba.add_word(f)

        add_msg_list=['早上好','上午好','中午好','下午好','晚上好','凌晨好','半夜好','午夜好','非常感谢',
                      '老师好','班主任好','主任好','班任好', '班班好']
        for w in add_msg_list:
            cls._local_jieba.add_word(w)


    #过滤，分词
    @classmethod
    def cutMsg(cls, mesg):
        # 替换规则
        for rule in cls.replace_FilterRule_list:
            r = re.compile(rule[0])
            mesg, n = r.subn(rule[1], mesg)

        # 删除规则
        for rule in cls.delete_FilterRule_list:
            r = re.compile(rule[0])
            mesg, n = r.subn('', mesg)

        p2 = re.compile(r'[^(\u4e00-\u9fa5)|\[|\]]')
        mesg = " ".join(p2.split(mesg)).strip()  # 取中文字符
        segs = []

        try:
            for seg in jieba.cut(mesg):
                if seg in cls.synonym_comon_dict.keys():
                    logger.debug("seg:%s" % seg)
                    # 同义词替换
                    seg = cls.synonym_base_dict[cls.synonym_comon_dict[seg]]
                #删除停止词与过滤词以及为空的分词
                if (seg not in cls.stopwords_dict)and (seg not in cls.filter_dict) and (seg != ' '):
                    segs.append(seg)
        except Exception as e:
            logger.error('handlemsg.cutMsg.synonym error: %s' % str(e))
            return ''
        return (" ".join(segs))

    # 过滤，分词
    @classmethod
    def cutMsg_word2vec(cls, mesg):
        # 替换规则
        for rule in cls.replace_FilterRule_list:
            r = re.compile(rule[0])
            mesg, n = r.subn(rule[1], mesg)

        # 删除规则
        for rule in cls.delete_FilterRule_list:
            r = re.compile(rule[0])
            mesg, n = r.subn('', mesg)

        p2 = re.compile(r'[^(\u4e00-\u9fa5)|\[|\]]')
        mesg = " ".join(p2.split(mesg)).strip()  # 取中文字符

        segs = []
        for seg in jieba.cut(mesg):
            if seg in cls.synonym_comon_dict.keys():
                logger.debug("seg:%s" % seg)
                # 近义词替换
                seg = cls.synonym_base_dict[cls.synonym_comon_dict[seg]]
            segs.append(seg)
        return (" ".join(segs))



    @classmethod
    def analysiscutMsg(cls, mesg):
        logger.info("mesg:%s" % mesg)

        # data结果的替换规则列表
        replacement_list = []
        # data结果的result
        result_list = []
        # 替换规则
        for rule in cls.replace_FilterRule_list:
            r = re.compile(rule[0])
            # 需要添加data信息时执行
            logger.info('_data !=1')
            m_findalls = r.findall(mesg)
            for m_findall in m_findalls:
                replacement_list.append({"rule": m_findall, "replace_val": rule[1]})
                result_list.append({"type":"1","word":m_findall,"replace_val":rule[1]})
            mesg, n = r.subn(rule[1], mesg)

        # 删除规则
        for rule in cls.delete_FilterRule_list:
            r = re.compile(rule[0])
            #需要添加data信息时执行
            m_findalls = r.findall(mesg)
            for m_findall in m_findalls:
                replacement_list.append({"rule": m_findall, "replace_val": ''})
                result_list.append({"type":"1","word":m_findall,"replace_val":''})
            mesg, n = r.subn('', mesg)

        logger.info("replacement_list in %s" % str(replacement_list))
        return_data = {}
        return_data['replacement'] = replacement_list

        p2 = re.compile(r'[^(\u4e00-\u9fa5)|\[|\]]')
        mesg = " ".join(p2.split(mesg)).strip()  # 取中文字符

        segs = []

        # data结果的同义词列表
        synonyms_list = []
        # data结果的停止词列表
        stop_list = []
        # data结果的过滤词列表
        filter_list = []
        # data结果的专业词列表
        technical_list = []
        for seg in jieba.cut(mesg):
            if seg in cls.synonym_comon_dict.keys():
                logger.debug("seg:%s" % seg)
                # 同义词替换
                seg_base = cls.synonym_base_dict[cls.synonym_comon_dict[seg]]
                # data结果的同义词列表添加信息
                synonyms_list.append({"rule": seg, "replace_val": seg_base})
                result_list.append({"type": "4", "word": seg, "replace_val": seg_base})
                segs.append(seg_base)
            # data结果的停止词列表添加信息
            elif seg in cls.stopwords_dict:
                stop_list.append(seg)
                result_list.append({"type": "3", "word": seg})
            # data结果的过滤词列表添加信息
            elif seg in cls.filter_dict:
                filter_list.append(seg)
                result_list.append({"type": "5", "word": seg})
            # data结果的专业词列表添加信息
            elif seg in cls.userdict:
                technical_list.append(seg)
                result_list.append({"type": "2", "word": seg})
                segs.append(seg)
            else:
                result_list.append({"type": "0", "word": seg})


        return_data['result'] = result_list
        return_data['aiword'] = segs
        return_data['synonyms'] = synonyms_list
        return_data['stop_word'] = stop_list
        return_data['technical_word'] = technical_list
        return_data['filter_word'] = filter_list

        return return_data


    #commin.py中getCategory2方法使用的只分词方法
    @classmethod
    def onlycutMsg(cls, mesg):
        p2 = re.compile(r'[^(\u4e00-\u9fa5)|(a-z)|(A-Z)|3Q|3q|\[|\]]')
        mesg = " ".join(p2.split(mesg)).strip()  # 取字符
        segs = []
        for seg in cls._local_jieba.cut(mesg):
            if seg != ' ':
                segs.append(seg)
        return segs


if __name__ == '__main__':
    aa = jieba.cut('退费')
    for a in aa:
        print (a)
    # print(HandleMsg.onlycutMsg('111'))
