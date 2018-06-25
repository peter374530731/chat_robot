#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import traceback
from sscp_py import views
from sscp_py.chatterbot import handlemsg, common
import re
from sscp_py.viewfunction import processSent2vec
from sscp_py.models import AiQuestion
from django.conf import settings


logger = logging.getLogger('django')
logger_req = logging.getLogger('django.request')
all_question_list = AiQuestion.objects.filter(is_del=0)
chat_value = float(settings.THRESHOLD)

p2 = re.compile(r'[^(\u4e00-\u9fa5)|\[|\]]')  # 正则获取中文与[]


# QA问答
def qafun(_question, robotId, status, top, com, robot_list, cos_list):
    return_list = []
    compare_dic = {}
    logger.info('qa _question :%s' % _question)

    try:
        get_category = common.getCategory(_question)  # 场景匹配

        # 匹配到场景以后将返回信息中添加一条场景信息
        if get_category['content'] != '':
            # 过滤词
            question = handlemsg.HandleMsg.cutMsg(_question)

            logger.info('qa.cutMsg:%s' % question)

            if robotId not in (robot_list.getrobot()).keys():
                logger.warning("qafun robotId:%s not in robot.Start_Robot.getrobot()" % str(robotId))
                views.config_all()

            _KVmsgs = ((robot_list.getrobot())[robotId])[status]

            com_dict = {}
            for msg in _KVmsgs:
                compare_value = com.compare(statement=question, other_statement=msg.knowledge['cut_question'])
                com_dict[msg.knowledge['question_id']] = compare_value
                compare_dic[msg.knowledge['question_id']] = msg.knowledge['question']

            # 按照字典中的value大小排序，并且去除前return_tuple_count个字典，转成元组
            return_tuple = sorted(com_dict.items(), key=lambda e: e[1], reverse=True)[:top]
            logger.info("return_tuple:%s" % str(return_tuple))

            return_list_items = []
            return_tuple_count = 0
            for _tuple in return_tuple:
                if _tuple[1] >= float(chat_value):
                    return_list_items.append(_tuple)
                    return_tuple_count = return_tuple_count + 1
            logger.info("return_list_items:%s" % str(return_list_items))
            cos_count = top - return_tuple_count
            if cos_count > 0:
                use_item = ((cos_list.getrobot())[robotId])[status]
                get_cos_list = cos_used(_question=get_category['content'], standardQuesVec=use_item.standardQuesVec,
                                        standardQuestion=use_item.standardQuestion, cut_question=use_item.cut_question,
                                        cos_question_ids=use_item.cos_question_ids, cos_count=cos_count)
                logger.info("get_cos_dict: %s" % str(get_cos_list))
                for get_cos_item in get_cos_list:
                    if get_cos_item['score'] >= float(chat_value):
                        return_list_items.append((get_cos_item['cos_question_id'], get_cos_item['score']))

            for _sotr in return_list_items:
                _question = compare_dic[_sotr[0]]
                _questionId = _sotr[0]
                _sotr = _sotr[1]
                return_list.append({'questionType': '0', 'question': _question, 'questionId': _questionId, 'score': _sotr})

            if len(return_list) == 0:
                return_list.append(
                    {'questionType': "无答案", 'question': '', 'questionId': '', 'score': '1'})

        else:
            return_list.append({'questionType': get_category['category'], 'question': '', 'questionId': '', 'score': '1'})
            return return_list

    except Exception as e:
        logger.error('qa ERROR:%s' % str(traceback.format_exc()))
        return []
    return return_list

#QA使用的词向量
def cos_used(_question, standardQuesVec, standardQuestion, cut_question, cos_question_ids, cos_count):
    cos_returns = processSent2vec.word2vec_fast(_question, standardQuesVec, cos_count)
    stu_cutMsg = cos_returns[0]

    return_list = []
    for cos_return in cos_returns[1]:
        score_and_index = {}
        score_and_index['cos_question_source'] = standardQuestion[cos_return[1]]  # 标准问题
        score_and_index['score'] = cos_return[0]  # 分数
        score_and_index['cos_cut'] = cut_question[cos_return[1]]  # 标准问题分词
        score_and_index['cos_student_cut'] = stu_cutMsg  # 学生问题分词
        score_and_index['cos_question_id'] = cos_question_ids[cos_return[1]]  # 匹配问题ID
        return_list.append(score_and_index)

    return return_list


#测例匹配方法
def ismatch(testdetail_item, com, r_srinit):
    get_data = qafun(_question=testdetail_item.example, robotId='0', status='1', top=1, com=com, robot_list=r_srinit)
    if len(get_data) == 0:
        return 0
    else:
        data_item = get_data[0]
        if data_item['questionType'] != '0':
            return 0
        else:
            _score = data_item['score']
            if float(_score) < chat_value:
                return 0
            else:
                current_questionId = data_item['questionId']
                get_questions = all_question_list.filter(question_id=int(current_questionId))
                for get_question in get_questions:
                    if get_question.parent_id == 0:
                        used_question_id = current_questionId
                    else:
                        used_question_id = get_question.parent_id
                    if int(testdetail_item.question_id) == int(used_question_id):
                        return 1
                    else:
                        return 0


# 测试用例执行方法
def configtestfun(record_Id,com,r_srinit):
    from sscp_py.models import AiTestDetail, AiTestRecord, AiTestResult
    import datetime
    global testcase_runling_dict
    try:
        testdetail_list = AiTestDetail.objects.filter(record_id=record_Id).order_by('question_id')
        logger.info("get AiTestDetail object coiunt=%d" % len(testdetail_list))

        return_dict = {'questionid': 0, 'matchcount': 0, 'nomatchcount': 0}

        totla_match_count = 0
        totla_nomathc_coiunt = 0

        current_question_id = 0
        for testdetail_item in testdetail_list:

            if current_question_id == 0:
                current_question_id = testdetail_item.question_id
            if testdetail_item.question_id == current_question_id:
                current_question_id=testdetail_item.question_id
                match_result = ismatch(_question=testdetail_item, com=com, robot_list=r_srinit)
                logger.info('match_result:%s' % str(match_result))
                if match_result==0:
                    return_dict["nomatchcount"] = return_dict["nomatchcount"] + 1
                    totla_nomathc_coiunt = totla_nomathc_coiunt + 1
                    testdetail_item.match_result = '不匹配'
                    testdetail_item.save()
                else:
                    testdetail_item.match_result='匹配'
                    testdetail_item.save()
                    return_dict["matchcount"] = return_dict["matchcount"] + 1
                    totla_match_count = totla_match_count + 1
            else:
                logger.info("add AiTestResult msg:record_id=%d,question_id=%d,match_count=%d,nomatch_count=%d" % (
                    record_Id, return_dict["questionid"], return_dict["matchcount"], return_dict["nomatchcount"]))
                add_to_resulr = AiTestResult(record_id=record_Id, question_id=current_question_id,
                                             match_count=return_dict["matchcount"],
                                             nomatch_count=return_dict["nomatchcount"])
                add_to_resulr.save()
                current_question_id = testdetail_item.question_id
                match_result = ismatch(_question=testdetail_item, com=com, robot_list=r_srinit)
                if match_result==0:
                    return_dict["nomatchcount"] = return_dict["nomatchcount"] + 1
                    totla_nomathc_coiunt = totla_nomathc_coiunt + 1
                    testdetail_item.match_result = '不匹配'
                    testdetail_item.save()
                else:
                    return_dict["matchcount"] = return_dict["matchcount"] + 1
                    totla_match_count = totla_match_count + 1
                    testdetail_item.match_result='匹配'
                    testdetail_item.save()

        logger.info("add AiTestResult msg:record_id=%d,question_id=%d,match_count=%d,nomatch_count=%d" % (
            record_Id, return_dict["questionid"], return_dict["matchcount"], return_dict["nomatchcount"]))

        if len(testdetail_list)>1:
            add_to_resulr = AiTestResult(record_id=record_Id, question_id=testdetail_item.question_id,
                                         match_count=return_dict["matchcount"],
                                         nomatch_count=return_dict["nomatchcount"])

            add_to_resulr.save()

        record_obj = AiTestRecord.objects.get(record_id=record_Id)
        record_obj.match_count = totla_match_count
        record_obj.nomatch_count = totla_nomathc_coiunt
        record_obj.end_time =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("add AiTestRecord msg:match_count=%d,nomatch_count=%d" % (totla_match_count, totla_nomathc_coiunt))
        record_obj.save()

        if str(record_Id) in testcase_runling_dict.keys():
            try:
                del testcase_runling_dict[str(record_Id)]

            except Exception as e:
                logger.error("delete key=%s in testcase_runling_dict error:" % (str(record_Id),str(e)))
    except Exception as e:
        logger.error('configtestfun error %s' % str(e))

    return 1

