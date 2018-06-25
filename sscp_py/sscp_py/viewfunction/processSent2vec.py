import jieba
import jieba.posseg as pseg
import logging
from gensim.models import word2vec
import numpy as np
import sys
from scipy.spatial.distance import pdist
import traceback
import re
from sscp_py.chatterbot import handlemsg


p2 = re.compile(r'[^(\u4e00-\u9fa5)|\[|\]]')

logging.basicConfig(format='%(asctime)s: %(levelname)s : %(message)s', level=logging.INFO)

w2v = word2vec.Word2Vec.load('/home/sscp_py/sscp_py/sscp_py/viewfunction/talkmodel/talkmodel_04_0524')
wordSize = 200
def sent2vec(s):
    words = s
    M = []
    with open("/home/sscp_py/sscp_py/sscp_py/viewfunction/talkmodel/words.txt", 'a') as f:           # 保存词向量模型里没有的词
        for w in words:
            try:
                if w == ' ':
                    continue
                M.append(w2v.wv[w])
                # print("{} vector is: {}".format(w, w2v.wv[w]))
            except:
                f.write(w+'\n')
                continue
    M = np.array(M)
    v = M.sum(axis = 0)
    if np.sqrt((v**2).sum()) < sys.float_info.epsilon:
        return v/0.1
    return v/np.sqrt((v ** 2).sum())

def convertSent2Vec(content):

    content_cut = jieba.cut(content)
    str = ' '.join(content_cut)
    vocabs = str.split()

    newline = sent2vec(vocabs)
    return newline

def convertSent2Vec_pseg(content):
    # print("the content is: {}".format(content))
    content_cut = pseg.cut(content)
    vocabs = []
    for vocab in content_cut:
        print("{}".format(vocab))
        if vocab.flag == 'r' or vocab.flag == 'uj' or vocab.flag == 'y':# or vocab.flag == 'x' or vocab.flag == 'y':
            continue
        else:
            vocabs.append(vocab.word)
    newline = sent2vec(vocabs)
    return newline

def EuclideanDistance(vec1, vec2):
    if isinstance(vec2, str) or isinstance(vec1, str):
        return 10
    dist = np.linalg.norm(vec1 - vec2)

    return dist

def cos_dist_bak(a, b):
    if a == ' ' or b == ' ':
        return 0.0
    aVec = sent2vec(a)
    bVec = sent2vec(b)
    if isinstance(aVec, np.float64) or isinstance(bVec, np.float64):
        return 0.0
    try:
        sims = 1 - pdist([aVec, bVec], 'cosine')
        return sims[0]
    except:
        print("{}".format(traceback.format_exc()))
        print("======================================a is: {}".format(a))
        print("======================================a type is: {}".format(type(aVec)))
        print("======================================b is: {}".format(b))
        print("======================================b type is: {}".format(type(bVec)))
        return 0.0

def cos_dist(a, b):
    if a == ' ' or b == ' ':
        return 0.0
    aVec = sent2vec(a)
    bVec = b
    if isinstance(aVec, np.float64) or isinstance(bVec, np.float64):
        return 0.0
    try:
        sims = 1 - pdist([aVec, bVec], 'cosine')
        return sims[0]
    except:
        print("{}".format(traceback.format_exc()))
        print("======================================a is: {}".format(a))
        print("======================================a type is: {}".format(type(aVec)))
        print("======================================b is: {}".format(b))
        print("======================================b type is: {}".format(type(bVec)))
        return 0.0

def word2vec_bak(sentence1,sentence2):
    sentence1 = " ".join(p2.split(sentence1)).strip()  # 取中文字符
    sentence2 = " ".join(p2.split(sentence2)).strip()  # 取中文字符
    cutMsg_msg1 = handlemsg.HandleMsg.cutMsg_word2vec(sentence1)
    cutMsg_msg2 = handlemsg.HandleMsg.cutMsg_word2vec(sentence2)
    cos = cos_dist_bak(cutMsg_msg1, cutMsg_msg2)
    cos = 2 * cos - 1
    return (sentence1, cutMsg_msg1, sentence2, cutMsg_msg2, cos)

def word2vec(aVec,bVec):
    if isinstance(aVec, np.float64) or isinstance(aVec, float) or isinstance(bVec, np.float64) or isinstance(bVec, float):
        cos = 0.0
    else:
        try:
            sims = 1 - pdist([aVec, bVec], 'cosine')
            cos = sims[0]
        except:
            print("{}".format(traceback.format_exc()))
            print("======================================a type is: {}".format(type(aVec)))
            print("======================================b type is: {}".format(type(bVec)))
            cos = 0.0
    cos = 2 * cos - 1
    return cos

def getVec(sentence):
    sentence = " ".join(p2.split(sentence)).strip()  # 取中文字符
    cutMsg_msg = handlemsg.HandleMsg.cutMsg_word2vec(sentence)
    if cutMsg_msg == ' ':
        aVec = 0.0
    else:
        aVec = sent2vec(cutMsg_msg)
        if isinstance(aVec, np.float64):
            aVec = 0.0
    return(aVec, cutMsg_msg)

def preprocessKnowledge(squestions):
    standardQestionVec = []                                          # 用来保存知识库的向量矩阵
    cutStandardQestion = []                                          # 用来保存知识库的分词结果
    for question in squestions:
        question = " ".join(p2.split(question)).strip() # 取中文字符
        cutMsg = handlemsg.HandleMsg.cutMsg_word2vec(question)       # 对知识库的问题进行预处理和分词
        cutStandardQestion.append(cutMsg)                            # 把分词后的知识库加到分词结果列表中
        questionVec = sent2vec(cutMsg)                               # 把知识库转换为句向量
        if isinstance(questionVec, np.float64):                      # 如果转换的结果是一个float值，把该向量赋值为指定维数的0值向量
            questionVec = [0.0 for i in range(wordSize)]
            # questionVec = 0.0
        else:
            questionVec = questionVec/(np.sqrt(np.sum(questionVec**2))) # 对问题向量做单位化
        standardQestionVec.append(questionVec)                       # 把单位化的向量添加进列表

    standardQestionVec = np.array(standardQestionVec)                # 把知识库列表转化成矩阵
    return (cutStandardQestion, standardQestionVec)                  # 返回分词后的知识库和知识库向量矩阵

def word2vec_fast(sentence, standardQestionVec, retNum):
    try:
        sentence = " ".join(p2.split(sentence)).strip()  # 取中文字符
        cutMsg_msg = handlemsg.HandleMsg.cutMsg_word2vec(sentence) # 学生问题进行预处理和分词
        msgVec = []
        ret = []
        msg = sent2vec(cutMsg_msg)                                 # 把分词完的句子转换成向量
        if isinstance(msg, np.float64):                            # 如果转换的结果是一个float值，把该向量赋值为指定维数的0值向量
            msg = [0.0 for i in range(wordSize)]
        else:
            msg = msg/(np.sqrt(np.sum(msg**2)))                    # 对问题向量做单位化
        msgVec.append(msg)
        msgVec = np.array(msgVec)
        msgVec = msgVec.transpose()                                # 把问题向量转化为Nx1维列向量
        cosine = np.dot(standardQestionVec, msgVec)                # 计算知识库和问题的余弦相似度
        for i in range(retNum):
            maxIndex = np.argmax(cosine)                               # 获取最大相似度的索引
            maxCos = cosine[maxIndex][0]                               # 获取最大的相似度
            maxCos = 2 * maxCos - 1                                    # 把相似度转换到0.8的阈值
            if maxCos < 0:                                             # 如果转换后的相似度小于0，就赋值为0
                maxCos = 0.0
            ret.append((maxCos, maxIndex))
            cosine[maxIndex][0] = 0.0
        return (cutMsg_msg, ret)                      # 返回分词的问题，最大相似度，最大相似度的索引
    except:
        print("{}".format(traceback.format_exc()))
        print("the msgVec is: {}".format(msgVec))



if __name__=="__main__":
    find_question = []
    with open("./fquestion_0508.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            find_question.append(line.strip('\n'))
    find_question_vector = []
    for index in range(len(find_question)):
        newLine = convertSent2Vec(find_question[index])
        find_question_vector.append(newLine)

    question = []
    with open("./question_0508.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            question.append(line.strip('\n'))
    totalNum = len(question)
    ErightNum = 0
    EwrongNum = 0
    CrightNum = 0
    CwrongNum = 0
    print("total number is: {}".format(totalNum))
    for i in range(1):
        qustLine = convertSent2Vec(question[i])
        minDis = 1
        minIndex = -1
        for index in range(len(find_question_vector)):
            distance = EuclideanDistance(qustLine, find_question_vector[index])
            if distance < minDis:
                minDis = distance
                minIndex = index
                # print("{} and {} euclidean distance is: {}".format(question[i], find_question[minIndex], minDis))
        # print("{} and {} euclidean distance is: {}".format(question, content, condistance))
        # print("{} is: {}".format("minimum index", minIndex))
        # print("{} and {} euclidean distance is: {}".format(question[i], find_question[minIndex], minDis))
        print("Euclidean {} is: {}".format(i, minIndex))
        if i == minIndex:
            ErightNum+=1
        else:
            EwrongNum+=1

        maxCos = 0
        maxIndex = -1
        for index in range(len(find_question_vector)):
            cos = cos_dist(qustLine, find_question_vector[index])
            if cos > maxCos:
                maxCos = cos
                maxIndex = index
                print("{} and {} cos distance is: {}".format(question[i], find_question[maxIndex], maxCos))

        # print("{} is: {}".format("maximum index", maxIndex))
        # print("{} and {} cos distance is: {}".format(question, test_content[maxIndex], maxCos))
        print("Cos {} is: {}".format(i, maxIndex))
        if i == maxIndex:
            CrightNum+=1
        else:
            CwrongNum+=1

    print("Euclidean precision is: {}", ErightNum/totalNum)
    print("Cos precisioin is: {}", CrightNum/totalNum)