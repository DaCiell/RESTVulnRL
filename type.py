import random
import string
import json
import Levenshtein

from logger import *
from RL.Q_Learning.RL_brain import QLearningTable
from constraint import PREDEFINED_DICT
from db import *


class Request_Parameter:
    def __init__(self, num: int, name: str, type: str, example: str, required: bool, readonly: bool, enum: list):
        self.num = num
        self.name = name
        self.type = type
        self.example = example
        self.required = required
        self.readonly = readonly
        self.enum = enum
        if self.type == 'String':
            self.val = 'aabbcc'
        elif self.type == 'Bool':
            self.val = True
        else:
            self.val = 1
        # todo:fixed类别
        if self.example:
            self.category = 'example'
            actions = ['example', 'predefined', 'success', 'request', 'response', 'random']
            self.initial_type_val = {'example': 0.0, 'predefined': 0.0, 'success': 0.0, 'request': 0.0, 'response': 0.0,
                                     'random': 0.0}
        else:
            self.category = 'random'
            actions = ['predefined', 'success', 'request', 'response', 'random']
            self.initial_type_val = {'predefined': 0.0, 'success': 0.0, 'request': 0.0, 'response': 0.0, 'random': 0.0}
        self.category_table = QLearningTable(actions=actions)
        self.request_table = None
        self.request_num = 0
        self.response_table = None
        self.response_num = 0
        self.initial_request_val = {}
        self.initial_response_val = {}

    def info(self):
        for name, value in vars(self).items():
            logger.info('\t%s=%s' % (name, value))
        logger.info('\t------------------------------------------------------------------')

    def init_request_table(self, num):
        # actions = [x for x in range(1, num + 1) if x != self.num]
        actions = [x for x in range(1, num + 1)]
        self.request_table = QLearningTable(actions=actions)

    def init_response_table(self, num):
        actions = [x for x in range(1, num + 1)]
        self.response_table = QLearningTable(actions=actions)

    def infer_predefined(self):
        if self.name == 'username':
            random_number = random.randint(100000, 999999)
            self.val = 'user' + str(random_number)
        elif self.name == 'password' or self.name == 'pwd':
            self.val = 'F9#j4L&w2@pE'
        elif self.name == 'email':
            random_number = random.randint(100000, 999999)
            self.val = 'email' + str(random_number) + '@outlook.com'
        elif 'url' in self.name:
            self.val = 'http://www.example.com'

    def initial_infer(self, request_parameters, response_parameters):
        # todo:只能与同一序列之前的参数作比较
        for request_parameter in request_parameters:
            if request_parameter.num != self.num:
                similarity_ratio = Levenshtein.ratio(self.name, request_parameter.name)
                self.initial_request_val[request_parameter.num] = similarity_ratio
                if similarity_ratio > 0.5:
                    self.initial_type_val['request'] = self.initial_type_val['request'] + 20 / len(request_parameters)

        for response_parameter in response_parameters:
            similarity_ratio = Levenshtein.ratio(self.name, response_parameter.name)
            self.initial_response_val[response_parameter.num] = similarity_ratio
            if similarity_ratio > 0.5:
                self.initial_type_val['response'] = self.initial_type_val['response'] + 20 / len(response_parameters)

    def choose_category(self, state, request_sequence, response_sequence):
        if len(self.enum) > 0:
            self.category = 'fixed'
            self.val = random.choice(self.enum)
            return
        excluded_actions = []
        if self.type == 'Property':
            self.category = 'fixed'
            self.val = {}
            return
        if not request_sequence:
            excluded_actions.append('request')
        if not response_sequence:
            excluded_actions.append('response')
        success_length = redis_conn.llen(self.num)
        if success_length == 0:
            excluded_actions.append('success')
        self.category = self.category_table.choose_action(state, self.initial_type_val, excluded_actions)
        if self.name in PREDEFINED_DICT:
            self.val = PREDEFINED_DICT[self.name]
            return
        if self.type == 'Bool':
            self.val = random.choice([True, False])
            return
        # if self.type == 'file':
        #     file_path = 'file/xss.pdf'
        #
        #     # 使用 'with' 语句确保文件在上传后关闭
        #     with open(file_path, 'rb') as f:
        #         # 创建文件字典
        #         files = {'attachment': f}
        if self.category == 'example':
            self.val = self.example
        elif self.category == 'predefined':
            if str(self.type).lower() == 'string':
                if random.random() < 0.9:
                    self.val = 'aabbcc'
                else:
                    self.val = ''
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = True
            else:
                self.val = 1
            self.infer_predefined()
        elif self.category == 'success':
            success_elements = redis_conn.lrange(self.num, 0, -1)
            random_element = random.choice(success_elements)
            # if self.type == 'string':
            #     self.val = str(random_element)
            # else:
            #     self.val = int(random_element)
            self.val = str(random_element)
        elif self.category == 'request':
            request_parameter = self.request_table.choose_action_restrict(state, self.initial_request_val,
                                                                          request_sequence)
            # print(request_parameter)
            self.request_num = request_parameter
            self.val = find_num(request_parameter, request_sequence)
            # print(self.val)
        elif self.category == 'response':
            response_parameter = self.response_table.choose_action_restrict(state, self.initial_response_val,
                                                                            response_sequence)
            self.response_num = response_parameter
            self.val = find_num(response_parameter, response_sequence)
        elif self.category == 'random' or self.val == '':
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)
        # print(self.val)

    def choose_category_random1(self, state, request_sequence, response_sequence):
        if len(self.enum) > 0:
            self.category = 'fixed'
            self.val = random.choice(self.enum)
            return
        excluded_actions = []
        if self.type == 'Property':
            self.category = 'fixed'
            self.val = {}
            return
        if not request_sequence:
            excluded_actions.append('request')
        if not response_sequence:
            excluded_actions.append('response')
        success_length = redis_conn.llen(self.num)
        if success_length == 0:
            excluded_actions.append('success')
        self.category = self.category_table.choose_action(state, self.initial_type_val, excluded_actions)
        if self.name in PREDEFINED_DICT:
            self.val = PREDEFINED_DICT[self.name]
            return
        if self.type == 'Bool':
            self.val = random.choice([True, False])
            return
        if self.category == 'example':
            self.val = self.example
        elif self.category == 'predefined':
            if str(self.type).lower() == 'string':
                if random.random() < 0.9:
                    self.val = 'aabbcc'
                else:
                    self.val = ''
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = True
            else:
                self.val = 1
            self.infer_predefined()
        elif self.category == 'success':
            success_elements = redis_conn.lrange(self.num, 0, -1)
            random_element = random.choice(success_elements)
            self.val = str(random_element)
        elif self.category == 'request':
            request_parameter = self.request_table.choose_action_restrict(state, self.initial_request_val,
                                                                          request_sequence)
            # print(request_parameter)
            self.request_num = request_parameter
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)
            # print(self.val)
        elif self.category == 'response':
            response_parameter = self.response_table.choose_action_restrict(state, self.initial_response_val,
                                                                            response_sequence)
            self.response_num = response_parameter
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)
        elif self.category == 'random' or self.val == '':
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)

    def choose_category_random2(self, state, request_sequence, response_sequence):
        if len(self.enum) > 0:
            self.category = 'fixed'
            self.val = random.choice(self.enum)
            return
        excluded_actions = []
        if self.type == 'Property':
            self.category = 'fixed'
            self.val = {}
            return
        if not request_sequence:
            excluded_actions.append('request')
        if not response_sequence:
            excluded_actions.append('response')
        success_length = redis_conn.llen(self.num)
        if success_length == 0:
            excluded_actions.append('success')
        self.category = self.category_table.choose_action(state, self.initial_type_val, excluded_actions)
        if self.name in PREDEFINED_DICT:
            self.val = PREDEFINED_DICT[self.name]
            return
        if self.type == 'Bool':
            self.val = random.choice([True, False])
            return
        if self.category == 'example':
            self.val = self.example
        elif self.category == 'predefined':
            if str(self.type).lower() == 'string':
                if random.random() < 0.9:
                    self.val = 'aabbcc'
                else:
                    self.val = ''
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = True
            else:
                self.val = 1
            self.infer_predefined()
        elif self.category == 'success':
            success_elements = redis_conn.lrange(self.num, 0, -1)
            random_element = random.choice(success_elements)
            self.val = str(random_element)
        elif self.category == 'request':
            request_parameter = self.request_table.choose_action_restrict(state, self.initial_request_val,
                                                                          request_sequence)
            # print(request_parameter)
            self.request_num = request_parameter
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)
            # print(self.val)
        elif self.category == 'response':
            response_parameter = self.response_table.choose_action_restrict(state, self.initial_response_val,
                                                                            response_sequence)
            self.response_num = response_parameter
            if str(self.type).lower() == 'string':
                characters = string.ascii_letters + string.digits
                # 从可选字符中随机选择生成指定长度的字符串
                random_string = ''.join(random.choice(characters) for _ in range(10))
                self.val = random_string
            elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
                self.val = random.choice([True, False])
            else:
                self.val = random.randint(1, 10000000)
        if str(self.type).lower() == 'string':
            characters = string.ascii_letters + string.digits
            # 从可选字符中随机选择生成指定长度的字符串
            random_string = ''.join(random.choice(characters) for _ in range(10))
            self.val = random_string
        elif str(self.type).lower() == 'bool' or str(self.type).lower() == 'boolean':
            self.val = random.choice([True, False])
        else:
            self.val = random.randint(1, 10000000)


class Response_Parameter:
    def __init__(self, num: int, name: str, type: int, example: str, enum: list, status_code: int):
        self.num = num
        self.name = name
        self.type = type
        self.example = example
        self.enum = enum
        self.status_code = status_code
        if self.type == 'String':
            self.val = 'aabbcc'
        elif self.type == 'Bool':
            self.val = True
        else:
            self.val = 1

    def info(self):
        for name, value in vars(self).items():
            logger.info('\t%s=%s' % (name, value))
        logger.info('\t------------------------------------------------------------------')


class Endpoint:
    def __init__(self, url: str, method: str, url_parameters: list, query_parameters: list, body_parameters: list,
                 header_parameters: list, body_type: str):
        self.url = url
        self.method = method
        self.url_parameters = url_parameters
        self.query_parameters = query_parameters
        self.body_parameters = body_parameters
        self.header_parameters = header_parameters
        self.response_parameters = []
        self.priority = 0
        self.body_type = body_type

    def info(self):
        logger.info(f'url={self.url}')
        logger.info(f'method={self.method}')
        logger.info(f'body_type={self.body_type}')

        if self.url_parameters:
            logger.info('url_parameters:')
            for url_parameter in self.url_parameters:
                url_parameter.info()
        else:
            logger.info('url_parameters: []')

        if self.query_parameters:
            logger.info('query_parameters:')
            for query_parameter in self.query_parameters:
                query_parameter.info()
        else:
            logger.info('query_parameters: []')

        if self.body_parameters:
            logger.info('body_parameters:')
            for body_parameter in self.body_parameters:
                body_parameter.info()
        else:
            logger.info('body_parameters: []')

        if self.header_parameters:
            logger.info('header_parameters:')
            for header_parameter in self.header_parameters:
                header_parameter.info()
        else:
            logger.info('header_parameters: []')

        if self.response_parameters:
            logger.info('response_parameters:')
            for header_parameter in self.response_parameters:
                header_parameter.info()
        else:
            logger.info('response_parameters: []')
        logger.info(
            '======================================================================================================')


class Sequence_Parmeter:
    # todo:加上name
    def __init__(self, num, val, name):
        self.num = num
        self.val = val
        self.name = name


class Sequence_Endpoint:
    def __init__(self, path, method, url, headers, body, category_dict, val_dict):
        self.path = path
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.category_dict = category_dict
        self.val_dict = val_dict


def find_num(num, sequence):
    # todo:序列中有多个num参数，选取哪一个
    for i in range(len(sequence)):
        if num == sequence[i].num:
            return sequence[i].val
