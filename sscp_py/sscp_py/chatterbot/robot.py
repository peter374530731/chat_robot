#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django')


class Robot(object):
    def __init__(self,_id,_knowledge_id,_knowledge):
        self.id=_id
        self.knowledgeid=_knowledge_id
        self.knowledge=_knowledge

class CosWordVectors(object):
    def __init__(self, standardQuestion, cut_question, standardQuesVec, cos_question_ids):
        self.standardQuestion = standardQuestion
        self.cut_question = cut_question
        self.standardQuesVec = standardQuesVec
        self.cos_question_ids = cos_question_ids

#当前已经实例化的知识库信息类
class Start_Robot(object):

    def __init__(self):
        logger.info("chatterbot>rebot>Start_Rpbot>__init__")
        self.robot_dict = {}

    def getrobot(self):
        logger.info("chatterbot>rebot>Start_Rpbot>getrobot")
        return self.robot_dict

    def addorchangerobot(self, robot_id, robot_obj):
        logger.info("chatterbot>rebot>Start_Rpbot>addorchangerobot:robot_id: %s" % robot_id)
        self.robot_dict[robot_id] = robot_obj

    def delrobot(self, robot_id):
        logger.info("chatterbot>rebot>Start_Rpbot>delrobot:robot_id: %s" % robot_id)
        del self.robot_dict[robot_id]
