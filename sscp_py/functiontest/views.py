#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from sscp_py.chatterbot import comparisons,common
import logging

logger = logging.getLogger('django')
logger_req = logging.getLogger('django.request')

#<editor-fold desc='场景测试'>
def question_function(_question,_robotId=175,_status=0):
    logger_req.info('request question :%s' % str(_question))
    try:
        get_category = common.getCategory(str(_question))  # 场景匹配
        if get_category['content'] == '':
            logger_req.info('finish changjing : %s' % _question)

        return get_category

    except Exception as e:
        logger.info('ERROR: %s' % str(e))
        response_data = {'ERROR': "response_data error"}
        return response_data

#感谢
test_list1= ["谢了",
             "谢你了",
             "谢您了",
             "谢谢你",
             "谢谢你的帮助",
             "谢谢您的帮助",
             "谢谢你老师",
             "谢谢老师你",
             "谢谢您",
             "谢谢您老师",
             "谢谢老师您",
             "谢谢老师",
             "老师谢谢",
             "老师谢谢你",
             "老师谢谢您",
             "谢谢美女（赞美）老师",
             "美女（赞美）老师谢谢",
             "谢谢王（姓）老师",
             "王（姓）老师谢谢",
             "太谢谢了",
             "太谢谢您了",
             "太谢谢你了",
             "太谢谢你了老师",
             "太谢谢您了老师",
             "太谢谢老师了",
             "太谢谢老师你了",
             "太谢谢老师您了",
             "太谢谢老师",
             "老师太谢谢了",
             "老师太谢谢你了",
             "老师太谢谢您了",
             "感谢您的帮助",
             "感谢你的帮助",
             "感谢",
             "感谢你",
             "感谢您",
             "感谢你老师",
             "感谢您老师",
             "老师感谢你",
             "老师感谢您",
             "老师感谢",
             "太感谢了",
             "太感谢你了",
             "太感谢你了老师",
             "太感谢您了",
             "太感谢您了老师",
             "老师太感谢了",
             "老师太感谢",
             "老师太感谢你了",
             "老师太感谢您了",
             "劳您费心！",
             "劳你费心",
             "费心",
             "费心了",
             "3Q",
             "Thank you",
             "劳驾了",
             "让您费心了",
             "实在过意不去",
             "拜托了",
             "麻烦您",
             "辛苦了老师",
             "老师辛苦了",
             "辛苦",
             "辛苦了"]

#问候
test_list2 = ["早",
              "早呀",
              "老师早上好",
              "早呀，老师",
              "早，老师",
              "老师，早",
              "早，班班",
              "早上好，班班",
              "班班早呀",
              "班班早上好",
              "早安",
              "good morning",
              "morning",
              "上午好",
              "上午好，老师。",
              "上午好呀，老师",
              "上午好，班班",
              "老师上午好",
              "老师，上午好呀",
              "班班上午好",
              "班班，上午好呀",
              "中午好",
              "老师，中午好",
              "班班，中午好",
              "中午好，老师",
              "中午好，班班",
              "午安",
              "老师，午安",
              "班班，午安",
              "午安，老师",
              "午安，班班",
              "中午好呀",
              "老师，中午好呀",
              "班班，中午好呀",
              "中午好呀，老师",
              "中午好呀，班班",
              "下午好",
              "老师，下午好",
              "班班，下午好",
              "下午好，老师",
              "下午好，班班",
              "下午好呀",
              "老师，下午好呀",
              "班班，下午好呀",
              "下午好呀，老师",
              "下午好呀，班班",
              "good afternoon",
              "good noon",
              "晚上好",
              "老师，晚上好",
              "班班，晚上好",
              "晚上好，老师",
              "晚上好，班班",
              "晚上好呀",
              "老师，晚上好呀",
              "班班，晚上好呀",
              "晚上好呀，老师",
              "晚上好呀，班班",
              "晚安",
              "老师，晚安",
              "班班，晚安",
              "晚安，班班",
              "晚安，老师",
              "晚安了",
              "晚安了，老师",
              "晚安了，班班",
              "老师，晚安了",
              "班班，晚安了",
              "我困了",
              "在？",
              "在？老师",
              "在？班班",
              "老师，在？",
              "班班，在？",
              "在吗",
              "老师在吗",
              "班班在吗",
              "在吗老师",
              "在吗班班",
              "亲爱的老师，在吗",
              "亲爱的班班，在吗",
              "在吗，亲爱的老师",
              "在吗，亲爱的班班",
              "你在吗",
              "老师，你在吗",
              "班班，你在吗",
              "班主任，你在吗",
              "您在吗",
              "老师，您在吗",
              "班班，您在吗",
              "您在吗？老师。",
              "您在吗？班班",
              "班班好",
              "老师好",
              "你好",
              "您好",
              "下班了吗",
              "老师，下班了吗",
              "班班，下班了吗",
              "下班了吗，老师",
              "下班了吗，班班",
              "亲爱的老师，下班了吗",
              "下班了吗，亲爱的老师",
              "亲爱的班班，下班了吗",
              "下班了吗？亲爱的班班",
              ]

#场景测试
def question(request):
    for test_item in test_list1:
        if question_function(test_item) == '':
            print('question:%s' % test_item)
    for test_item in test_list2:
        if question_function(test_item) == '':
            print('question:%s' % test_item)
    return HttpResponse('ok')
#</editor-fold>


