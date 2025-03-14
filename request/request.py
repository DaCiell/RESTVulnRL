import json
import random
import re

import requests

from constraint import REGISTER_LIST, PREDEFINED_DICT
from type import Endpoint, Sequence_Parmeter, Sequence_Endpoint
from db import *
from logger import *


def request_single(base_url, endpoint: Endpoint, request_sequence, response_sequence):
    url_parameters = endpoint.url_parameters
    query_parameters = endpoint.query_parameters
    body_parameters = endpoint.body_parameters
    header_parameters = endpoint.header_parameters
    observation = 'init'
    result_request_sequence = []
    file_flag = False
    logger.info('=====================================================================================================')

    for url_parameter in endpoint.url_parameters:
        url_parameter.initial_infer(request_sequence, response_sequence)
    for query_parameter in endpoint.query_parameters:
        query_parameter.initial_infer(request_sequence, response_sequence)
    for header_parameter in endpoint.header_parameters:
        header_parameter.initial_infer(request_sequence, response_sequence)
    for body_parameter in endpoint.body_parameters:
        body_parameter.initial_infer(request_sequence, response_sequence)

    logger.info(f'Endpoint: {endpoint.url}, {endpoint.method}, {endpoint.priority}')
    for url_parameter in url_parameters:
        url_parameter.choose_category_random2(observation, request_sequence, response_sequence)
        sequence_parameter = Sequence_Parmeter(url_parameter.num, url_parameter.val, url_parameter.name)
        if len(str(url_parameter.val)) < 200:
            result_request_sequence.append(sequence_parameter)
        logger.info(
            f'URL parameter: {url_parameter.num}, {url_parameter.name}, {url_parameter.category}, {url_parameter.val}')
        if url_parameter.type == 'file':
            file_flag = True
    for query_parameter in query_parameters:
        query_parameter.choose_category_random2(observation, request_sequence, response_sequence)
        sequence_parameter = Sequence_Parmeter(query_parameter.num, query_parameter.val, query_parameter.name)
        if len(str(query_parameter.val)) < 200:
            result_request_sequence.append(sequence_parameter)
        logger.info(
            f'Query parameter: {query_parameter.num}, {query_parameter.name}, {query_parameter.category}, {query_parameter.val}')
        if query_parameter.type == 'file':
            file_flag = True
    for body_parameter in body_parameters:
        body_parameter.choose_category_random2(observation, request_sequence, response_sequence)
        sequence_parameter = Sequence_Parmeter(body_parameter.num, body_parameter.val, body_parameter.name)
        if len(str(body_parameter.val)) < 200:
            result_request_sequence.append(sequence_parameter)
        logger.info(
            f'Body parameter: {body_parameter.num}, {body_parameter.name}, {body_parameter.category}, {body_parameter.val}')
        if body_parameter.type == 'file':
            file_flag = True
    for header_parameter in header_parameters:
        header_parameter.choose_category_random2(observation, request_sequence, response_sequence)
        sequence_parameter = Sequence_Parmeter(header_parameter.num, header_parameter.val, header_parameter.name)
        if len(str(header_parameter.val)) < 200:
            result_request_sequence.append(sequence_parameter)
        logger.info(
            f'Header parameter: {header_parameter.num}, {header_parameter.name}, {header_parameter.category}, {header_parameter.val}')
        if header_parameter.type == 'file':
            file_flag = True

    url = base_url + endpoint.url
    method = endpoint.method
    matches = re.findall(r'\{([^}]+)\}', url)
    for match in matches:
        for url_parameter in url_parameters:
            if url_parameter.name == match:
                url = url.replace('{' + match + '}', str(url_parameter.val))

    headers = {
        'Content-Type': 'application/json'
    }
    if header_parameters:
        for header_parameter in header_parameters:
            headers[header_parameter.name] = header_parameter.val

    if query_parameters:
        url = url + '?'
        for query_parameter in query_parameters:
            url = url + query_parameter.name + '=' + str(query_parameter.val)
            if query_parameters.index(query_parameter) != len(query_parameters) - 1:
                url = url + '&'

    if endpoint.body_type == 'object':
        payload = {}
        for body_parameter in body_parameters:
            payload[body_parameter.name] = body_parameter.val
    else:
        payload = []
        payload_item = {}
        for body_parameter in body_parameters:
            payload_item[body_parameter.name] = body_parameter.val
        payload.append(payload_item)
    flag = True
    response = None
    if not file_flag:
        if AUTH:
            try:
                if method == 'head':
                    response = requests.head(url=url, headers=headers, timeout=10, auth=(USERNAME, PASSWORD))
                if method == 'get':
                    response = requests.get(url=url, headers=headers, timeout=10, auth=(USERNAME, PASSWORD))
                if method == 'post':
                    response = requests.post(url=url, headers=headers, json=payload, timeout=10,
                                             auth=(USERNAME, PASSWORD))
                if method == 'put':
                    response = requests.put(url=url, headers=headers, json=payload, timeout=10,
                                            auth=(USERNAME, PASSWORD))
                if method == 'patch':
                    response = requests.patch(url=url, headers=headers, json=payload, timeout=10,
                                              auth=(USERNAME, PASSWORD))
                if method == 'delete':
                    response = requests.delete(url=url, headers=headers, timeout=10, auth=(USERNAME, PASSWORD))
            except:
                flag = False
                response = None
        else:
            try:
                if method == 'head':
                    response = requests.head(url=url, headers=headers, timeout=10)
                if method == 'get':
                    response = requests.get(url=url, headers=headers, timeout=10)
                if method == 'post':
                    response = requests.post(url=url, headers=headers, json=payload, timeout=10)
                if method == 'put':
                    response = requests.put(url=url, headers=headers, json=payload, timeout=10)
                if method == 'patch':
                    response = requests.patch(url=url, headers=headers, json=payload, timeout=10)
                if method == 'delete':
                    response = requests.delete(url=url, headers=headers, timeout=10)
            except:
                flag = False
                response = None
    else:
        file_path = 'file/xss.pdf'

        with open(file_path, 'rb') as f:
            files = {'attachment': f}
            if AUTH:
                try:
                    if method == 'get':
                        response = requests.get(url=url, headers=headers, timeout=10, auth=(USERNAME, PASSWORD),
                                                files=files)
                    if method == 'post':
                        response = requests.post(url=url, headers=headers, json=payload, timeout=10,
                                                 auth=(USERNAME, PASSWORD), files=files)
                    if method == 'put':
                        response = requests.put(url=url, headers=headers, json=payload, timeout=10,
                                                auth=(USERNAME, PASSWORD), files=files)
                    if method == 'delete':
                        response = requests.delete(url=url, headers=headers, timeout=10, auth=(USERNAME, PASSWORD),
                                                   files=files)
                except:
                    flag = False
                    response = None
            else:
                try:
                    if method == 'get':
                        response = requests.get(url=url, headers=headers, timeout=10, files=files)
                    if method == 'post':
                        response = requests.post(url=url, headers=headers, json=payload, timeout=10, files=files)
                    if method == 'put':
                        response = requests.put(url=url, headers=headers, json=payload, timeout=10, files=files)
                    if method == 'delete':
                        response = requests.delete(url=url, headers=headers, timeout=10, files=files)
                except:
                    flag = False
                    response = None
    return flag, response, result_request_sequence


def request_priority(endpoint: Endpoint):
    if endpoint.method == 'post':
        priority = 60
    elif endpoint.method == 'delete':
        priority = 10
    else:
        priority = 30

    return priority


def update_redis(parameters):
    for parameter in parameters:
        redis_conn.rpush(parameter.num, str(parameter.val))


def check_response(response):
    if response == None:
        return False
    if response.status_code >= 400:
        return False
    content_type = response.headers.get('Content-Type')
    if content_type and (content_type.startswith('image/') or content_type == 'application/octet-stream'):
        return True
    if not response.text:
        return True
    try:
        response_text = json.loads(response.text)
    except:
        return False
    if type(response_text) == list:
        return True
    elif type(response_text) == dict:
        for name, val in response_text.items():
            if name == 'status':
                if val == 'fail':
                    return False
            if name == 'success':
                if val == 'false':
                    return False
        return True


def endpoint_sequence_duplicate(endpoint_sequence):
    result = []
    i = 0
    while i < len(endpoint_sequence):
        if i == len(endpoint_sequence) - 1 or not (
                endpoint_sequence[i].method == endpoint_sequence[i + 1].method and endpoint_sequence[i].url ==
                endpoint_sequence[i + 1].url):
            result.append(endpoint_sequence[i])
        i += 1
    return result


def request_sequence(base_url, endpoints):
    for endpoint in endpoints:
        priority = request_priority(endpoint)
        endpoint.priority = priority

    success_endpoints = []
    error_endpoints = []

    request_sequence = []
    response_sequence = []
    endpoint_sequence = []
    state = 'init'

    prior_endpoints = filter(lambda x: x.priority >= 90, endpoints)
    prior_endpoints = sorted(prior_endpoints, key=lambda x: x.priority, reverse=True)
    i = 0
    while i < len(prior_endpoints):
        prior_endpoint = prior_endpoints[i]
        flag, response, temp_request_sequence = request_single(base_url, prior_endpoint, request_sequence,
                                                               response_sequence)
        if response != None:
            request_log(response)

        if not flag or not check_response(response):
            reward = -1
        else:
            reward = 1
            temp_endpoint = prior_endpoint.method + ' ' + prior_endpoint.url
            if temp_endpoint not in success_endpoints:
                success_endpoints.append(temp_endpoint)

        response_text = None
        if response:
            content_type = response.headers.get('Content-Type')
        else:
            content_type = None

        if content_type and content_type.startswith('image/'):
            new_state = 'picture'
        else:
            try:
                response_text = json.loads(response.text)
                new_state = str(response.status_code)
                for name, val in response_text.items():
                    new_state = new_state + '-||' + str(val) + '||'
            except:
                new_state = '500'

        category_dict = {}
        val_dict = {}
        for url_parameter in prior_endpoint.url_parameters:
            if url_parameter.type == 'Bool':
                continue
            if url_parameter.name in PREDEFINED_DICT:
                continue
            if url_parameter.category == 'fixed':
                continue
            url_parameter.category_table.learn(state, url_parameter.category, reward,
                                               new_state, url_parameter.initial_type_val)
            category_dict[url_parameter.name] = url_parameter.category
            val_dict[url_parameter.name] = url_parameter.val
            if url_parameter.category == 'request':
                url_parameter.request_table.learn(state, url_parameter.request_num, reward,
                                                  new_state, url_parameter.initial_request_val)
            if url_parameter.category == 'response':
                url_parameter.response_table.learn(state, url_parameter.response_num, reward,
                                                   new_state, url_parameter.initial_response_val)
        for query_parameter in prior_endpoint.query_parameters:
            if query_parameter.type == 'Bool':
                continue
            if query_parameter.name in PREDEFINED_DICT:
                continue
            if query_parameter.category == 'fixed':
                continue
            query_parameter.category_table.learn(state, query_parameter.category, reward,
                                                 new_state, query_parameter.initial_type_val)
            category_dict[query_parameter.name] = query_parameter.category
            val_dict[query_parameter.name] = query_parameter.val
            if query_parameter.category == 'request':
                query_parameter.request_table.learn(state, query_parameter.request_num, reward,
                                                    new_state, query_parameter.initial_request_val)
            if query_parameter.category == 'response':
                query_parameter.response_table.learn(state, query_parameter.response_num, reward,
                                                     new_state, query_parameter.initial_response_val)
        for header_parameter in prior_endpoint.header_parameters:
            if header_parameter.type == 'Bool':
                continue
            if header_parameter.name in PREDEFINED_DICT:
                continue
            if header_parameter.category == 'fixed':
                continue
            header_parameter.category_table.learn(state, header_parameter.category, reward,
                                                  new_state, header_parameter.initial_type_val)
            category_dict[header_parameter.name] = header_parameter.category
            val_dict[header_parameter.name] = header_parameter.val
            if header_parameter.category == 'request':
                header_parameter.request_table.learn(state, header_parameter.request_num, reward,
                                                     new_state, header_parameter.initital_request_val)
            if header_parameter.category == 'response':
                header_parameter.response_table.learn(state, header_parameter.response_num, reward,
                                                      new_state, header_parameter.initial_response_val)
        for body_parameter in prior_endpoint.body_parameters:
            if body_parameter.type == 'Bool':
                continue
            if body_parameter.name in PREDEFINED_DICT:
                continue
            if body_parameter.category == 'fixed':
                continue
            body_parameter.category_table.learn(state, body_parameter.category, reward,
                                                new_state, body_parameter.initial_type_val)
            category_dict[body_parameter.name] = body_parameter.category
            val_dict[body_parameter.name] = body_parameter.val
            if body_parameter.category == 'request':
                body_parameter.request_table.learn(state, body_parameter.request_num, reward,
                                                   new_state, body_parameter.initial_request_val)
            if body_parameter.category == 'response':
                body_parameter.response_table.learn(state, body_parameter.response_num, reward,
                                                    new_state, body_parameter.initial_response_val)

        if not flag or not check_response(response):
            if response == None:
                continue
            if flag and response.status_code >= 500:
                sequence_endpoint = Sequence_Endpoint(prior_endpoint.url, response.request.method, response.request.url,
                                                      dict(response.request.headers), response.request.body.decode(
                        'utf-8') if response.request.body else None, category_dict, val_dict)
                error_endpoints.append(sequence_endpoint)

            continue
        else:
            i = i + 1
            request_sequence.extend(temp_request_sequence)
            update_redis(prior_endpoint.url_parameters)
            update_redis(prior_endpoint.query_parameters)
            update_redis(prior_endpoint.header_parameters)
            update_redis(prior_endpoint.body_parameters)

            sequence_endpoint = Sequence_Endpoint(prior_endpoint.url, response.request.method, response.request.url,
                                                  dict(response.request.headers), response.request.body.decode(
                    'utf-8') if response.request.body else None, category_dict, val_dict)
            endpoint_sequence.append(sequence_endpoint)

        if response_text:
            if type(response_text) == dict:
                for name, val in response_text.items():
                    for response_parameter in prior_endpoint.response_parameters:
                        if response_parameter.name == name:
                            if len(str(val)) < 200:
                                response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val, name)
                                response_sequence.append(response_sequence_parameter)
            elif type(response_text) == list:
                for response_text_ in response_text:
                    try:
                        for name, val in response_text_.items():
                            for response_parameter in prior_endpoint.response_parameters:
                                if response_parameter.name == name:
                                    if len(str(val)) < 200:
                                        response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val,
                                                                                        name)
                                        response_sequence.append(response_sequence_parameter)
                    except:
                        pass

    post_endpoints = list(filter(lambda x: x.priority == 60, endpoints))
    i = 0
    while i < 5:
        if len(post_endpoints) == 0:
            break
        post_endpoint = random.choice(post_endpoints)
        flag, response, temp_request_sequence = request_single(base_url, post_endpoint, request_sequence,
                                                               response_sequence)
        if response != None:
            request_log(response)
        i = i + 1

        if not flag or not check_response(response):
            reward = -1
        else:
            reward = 1
            temp_endpoint = post_endpoint.method + ' ' + post_endpoint.url
            if temp_endpoint not in success_endpoints:
                success_endpoints.append(temp_endpoint)

        response_text = None
        if response:
            content_type = response.headers.get('Content-Type')
        else:
            content_type = None

        if content_type and content_type.startswith('image/'):
            new_state = 'picture'
        else:
            try:
                response_text = json.loads(response.text)
                new_state = str(response.status_code)
                for name, val in response_text.items():
                    new_state = new_state + '-||' + str(val) + '||'
            except:
                new_state = '500'

        category_dict = {}
        val_dict = {}
        for url_parameter in post_endpoint.url_parameters:
            if url_parameter.type == 'Bool':
                continue
            if url_parameter.name in PREDEFINED_DICT:
                continue
            if url_parameter.category == 'fixed':
                continue
            url_parameter.category_table.learn(state, url_parameter.category, reward,
                                               new_state, url_parameter.initial_type_val)
            category_dict[url_parameter.name] = url_parameter.category
            val_dict[url_parameter.name] = url_parameter.val
            if url_parameter.category == 'request':
                url_parameter.request_table.learn(state, url_parameter.request_num, reward,
                                                  new_state, url_parameter.initial_request_val)
            if url_parameter.category == 'response':
                url_parameter.response_table.learn(state, url_parameter.response_num, reward,
                                                   new_state, url_parameter.initial_response_val)
        for query_parameter in post_endpoint.query_parameters:
            if query_parameter.type == 'Bool':
                continue
            if query_parameter.name in PREDEFINED_DICT:
                continue
            if query_parameter.category == 'fixed':
                continue
            query_parameter.category_table.learn(state, query_parameter.category, reward,
                                                 new_state, query_parameter.initial_type_val)
            category_dict[query_parameter.name] = query_parameter.category
            val_dict[query_parameter.name] = query_parameter.val
            if query_parameter.category == 'request':
                query_parameter.request_table.learn(state, query_parameter.request_num, reward,
                                                    new_state, query_parameter.initial_request_val)
            if query_parameter.category == 'response':
                query_parameter.response_table.learn(state, query_parameter.response_num, reward,
                                                     new_state, query_parameter.initial_response_val)
        for header_parameter in post_endpoint.header_parameters:
            if header_parameter.type == 'Bool':
                continue
            if header_parameter.name in PREDEFINED_DICT:
                continue
            if header_parameter.category == 'fixed':
                continue
            header_parameter.category_table.learn(state, header_parameter.category, reward,
                                                  new_state, header_parameter.initial_type_val)
            category_dict[header_parameter.name] = header_parameter.category
            val_dict[header_parameter.name] = header_parameter.val
            if header_parameter.category == 'request':
                header_parameter.request_table.learn(state, header_parameter.request_num, reward,
                                                     new_state, header_parameter.initial_request_val)
            if header_parameter.category == 'response':
                header_parameter.response_table.learn(state, header_parameter.response_num, reward,
                                                      new_state, header_parameter.initial_response_val)
        for body_parameter in post_endpoint.body_parameters:
            if body_parameter.type == 'Bool':
                continue
            if body_parameter.name in PREDEFINED_DICT:
                continue
            if body_parameter.category == 'fixed':
                continue
            body_parameter.category_table.learn(state, body_parameter.category, reward,
                                                new_state, body_parameter.initial_type_val)
            category_dict[body_parameter.name] = body_parameter.category
            val_dict[body_parameter.name] = body_parameter.val
            if body_parameter.category == 'request':
                body_parameter.request_table.learn(state, body_parameter.request_num, reward,
                                                   new_state, body_parameter.initial_request_val)
            if body_parameter.category == 'response':
                body_parameter.response_table.learn(state, body_parameter.response_num, reward,
                                                    new_state, body_parameter.initial_response_val)

        if not flag or not check_response(response):
            if response == None:
                continue
            if flag and response.status_code >= 500:
                sequence_endpoint = Sequence_Endpoint(post_endpoint.url, response.request.method, response.request.url,
                                                      dict(response.request.headers), response.request.body.decode(
                        'utf-8') if response.request.body else None, category_dict, val_dict)
                error_endpoints.append(sequence_endpoint)

            continue
        else:
            i = i + random.randint(1, 20)
            request_sequence.extend(temp_request_sequence)
            update_redis(post_endpoint.url_parameters)
            update_redis(post_endpoint.query_parameters)
            update_redis(post_endpoint.header_parameters)
            update_redis(post_endpoint.body_parameters)

            sequence_endpoint = Sequence_Endpoint(post_endpoint.url, response.request.method, response.request.url,
                                                  dict(response.request.headers), response.request.body.decode(
                    'utf-8') if response.request.body else None, category_dict, val_dict)
            endpoint_sequence.append(sequence_endpoint)

        if response_text:
            if type(response_text) == dict:
                for name, val in response_text.items():
                    for response_parameter in post_endpoint.response_parameters:
                        if response_parameter.name == name:
                            if len(str(val)) < 200:
                                response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val, name)
                                response_sequence.append(response_sequence_parameter)
            elif type(response_text) == list:
                for response_text_ in response_text:
                    try:
                        for name, val in response_text_.items():
                            for response_parameter in post_endpoint.response_parameters:
                                if response_parameter.name == name:
                                    if len(str(val)) < 200:
                                        response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val,
                                                                                        name)
                                        response_sequence.append(response_sequence_parameter)
                    except:
                        pass

    operation_endpoints = list(filter(lambda x: x.priority == 30, endpoints))
    i = 0
    while i < 10:
        if len(operation_endpoints) == 0:
            break
        operation_endpoint = random.choice(operation_endpoints)
        flag, response, temp_request_sequence = request_single(base_url, operation_endpoint, request_sequence,
                                                               response_sequence)
        if response != None:
            request_log(response)
        i = i + 1

        if not flag or not check_response(response):
            reward = -1
        else:
            reward = 1
            temp_endpoint = operation_endpoint.method + ' ' + operation_endpoint.url
            if temp_endpoint not in success_endpoints:
                success_endpoints.append(temp_endpoint)

        response_text = None
        if response:
            content_type = response.headers.get('Content-Type')
        else:
            content_type = None

        if content_type and content_type.startswith('image/'):
            new_state = 'picture'
        else:
            try:
                response_text = json.loads(response.text)
                new_state = str(response.status_code)
                for name, val in response_text.items():
                    new_state = new_state + '-||' + str(val) + '||'
            except:
                new_state = '500'

        if response and response.content and len(response.content) > 1000:
            pass

        category_dict = {}
        val_dict = {}
        for url_parameter in operation_endpoint.url_parameters:
            if url_parameter.type == 'Bool':
                continue
            if url_parameter.name in PREDEFINED_DICT:
                continue
            if url_parameter.category == 'fixed':
                continue
            url_parameter.category_table.learn(state, url_parameter.category, reward,
                                               new_state, url_parameter.initial_type_val)
            category_dict[url_parameter.name] = url_parameter.category
            val_dict[url_parameter.name] = url_parameter.val
            if url_parameter.category == 'request':
                url_parameter.request_table.learn(state, url_parameter.request_num, reward,
                                                  new_state, url_parameter.initial_request_val)
            if url_parameter.category == 'response':
                url_parameter.response_table.learn(state, url_parameter.response_num, reward,
                                                   new_state, url_parameter.initial_response_val)
        for query_parameter in operation_endpoint.query_parameters:
            if query_parameter.type == 'Bool':
                continue
            if query_parameter.name in PREDEFINED_DICT:
                continue
            if query_parameter.category == 'fixed':
                continue
            query_parameter.category_table.learn(state, query_parameter.category, reward,
                                                 new_state, query_parameter.initial_type_val)
            category_dict[query_parameter.name] = query_parameter.category
            val_dict[query_parameter.name] = query_parameter.val
            if query_parameter.category == 'request':
                query_parameter.request_table.learn(state, query_parameter.request_num, reward,
                                                    new_state, query_parameter.initial_request_val)
            if query_parameter.category == 'response':
                query_parameter.response_table.learn(state, query_parameter.response_num, reward,
                                                     new_state, query_parameter.initial_response_val)
        for header_parameter in operation_endpoint.header_parameters:
            if header_parameter.type == 'Bool':
                continue
            if header_parameter.name in PREDEFINED_DICT:
                continue
            if header_parameter.category == 'fixed':
                continue
            header_parameter.category_table.learn(state, header_parameter.category, reward,
                                                  new_state, header_parameter.initial_type_val)
            category_dict[header_parameter.name] = header_parameter.category
            val_dict[header_parameter.name] = header_parameter.val
            if header_parameter.category == 'request':
                header_parameter.request_table.learn(state, header_parameter.request_num, reward,
                                                     new_state, header_parameter.initial_request_val)
            if header_parameter.category == 'response':
                header_parameter.response_table.learn(state, header_parameter.response_num, reward,
                                                      new_state, header_parameter.initial_response_val)
        for body_parameter in operation_endpoint.body_parameters:
            if body_parameter.type == 'Bool':
                continue
            if body_parameter.name in PREDEFINED_DICT:
                continue
            if body_parameter.category == 'fixed':
                continue
            body_parameter.category_table.learn(state, body_parameter.category, reward,
                                                new_state, body_parameter.initial_type_val)
            category_dict[body_parameter.name] = body_parameter.category
            val_dict[body_parameter.name] = body_parameter.val
            if body_parameter.category == 'request':
                body_parameter.request_table.learn(state, body_parameter.request_num, reward,
                                                   new_state, body_parameter.initial_request_val)
            if body_parameter.category == 'response':
                body_parameter.response_table.learn(state, body_parameter.response_num, reward,
                                                    new_state, body_parameter.initial_response_val)

        if not flag or not check_response(response):
            if response == None:
                continue
            if flag and response.status_code >= 500:
                sequence_endpoint = Sequence_Endpoint(operation_endpoint.url, response.request.method,
                                                      response.request.url,
                                                      dict(response.request.headers), response.request.body.decode(
                        'utf-8') if response.request.body else None, category_dict, val_dict)
                error_endpoints.append(sequence_endpoint)

            continue
        else:
            i = i + random.randint(1, 20)
            request_sequence.extend(temp_request_sequence)
            update_redis(operation_endpoint.url_parameters)
            update_redis(operation_endpoint.query_parameters)
            update_redis(operation_endpoint.header_parameters)
            update_redis(operation_endpoint.body_parameters)

            sequence_endpoint = Sequence_Endpoint(operation_endpoint.url, response.request.method, response.request.url,
                                                  dict(response.request.headers), response.request.body.decode(
                    'utf-8') if response.request.body else None, category_dict, val_dict)
            endpoint_sequence.append(sequence_endpoint)

        if response_text:
            if type(response_text) == dict:
                for name, val in response_text.items():
                    for response_parameter in operation_endpoint.response_parameters:
                        if response_parameter.name == name:
                            if len(str(val)) < 200:
                                response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val, name)
                                response_sequence.append(response_sequence_parameter)
            elif type(response_text) == list:
                for response_text_ in response_text:
                    try:
                        for name, val in response_text_.items():
                            for response_parameter in operation_endpoint.response_parameters:
                                if response_parameter.name == name:
                                    if len(str(val)) < 200:
                                        response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val,
                                                                                        name)
                                        response_sequence.append(response_sequence_parameter)
                    except:
                        pass

    delete_endpoints = list(filter(lambda x: x.priority == 10, endpoints))
    i = 0
    while i < 3:
        if len(delete_endpoints) == 0:
            break
        delete_endpoint = random.choice(delete_endpoints)
        flag, response, temp_request_sequence = request_single(base_url, delete_endpoint, request_sequence,
                                                               response_sequence)
        if response != None:
            request_log(response)
        i = i + 1

        if not flag or not check_response(response):
            reward = -1
        else:
            reward = 1
            temp_endpoint = delete_endpoint.method + ' ' + delete_endpoint.url
            if temp_endpoint not in success_endpoints:
                success_endpoints.append(temp_endpoint)

        response_text = None
        if response:
            content_type = response.headers.get('Content-Type')
        else:
            content_type = None

        if content_type and content_type.startswith('image/'):
            new_state = 'picture'
        else:
            try:
                response_text = json.loads(response.text)
                new_state = str(response.status_code)
                for name, val in response_text.items():
                    new_state = new_state + '-||' + str(val) + '||'
            except:
                new_state = '500'

        category_dict = {}
        val_dict = {}
        for url_parameter in delete_endpoint.url_parameters:
            if url_parameter.type == 'Bool':
                continue
            if url_parameter.name in PREDEFINED_DICT:
                continue
            if url_parameter.category == 'fixed':
                continue
            url_parameter.category_table.learn(state, url_parameter.category, reward,
                                               new_state, url_parameter.initial_type_val)
            category_dict[url_parameter.name] = url_parameter.category
            val_dict[url_parameter.name] = url_parameter.val
            if url_parameter.category == 'request':
                url_parameter.request_table.learn(state, url_parameter.request_num, reward,
                                                  new_state, url_parameter.initial_request_val)
            if url_parameter.category == 'response':
                url_parameter.response_table.learn(state, url_parameter.response_num, reward,
                                                   new_state, url_parameter.initial_response_val)
        for query_parameter in delete_endpoint.query_parameters:
            if query_parameter.type == 'Bool':
                continue
            if query_parameter.name in PREDEFINED_DICT:
                continue
            if query_parameter.category == 'fixed':
                continue
            query_parameter.category_table.learn(state, query_parameter.category, reward,
                                                 new_state, query_parameter.initial_type_val)
            category_dict[query_parameter.name] = query_parameter.category
            val_dict[query_parameter.name] = query_parameter.val
            if query_parameter.category == 'request':
                query_parameter.request_table.learn(state, query_parameter.request_num, reward,
                                                    new_state, query_parameter.initial_request_val)
            if query_parameter.category == 'response':
                query_parameter.response_table.learn(state, query_parameter.response_num, reward,
                                                     new_state, query_parameter.initial_response_val)
        for header_parameter in delete_endpoint.header_parameters:
            if header_parameter.type == 'Bool':
                continue
            if header_parameter.name in PREDEFINED_DICT:
                continue
            if header_parameter.category == 'fixed':
                continue
            header_parameter.category_table.learn(state, header_parameter.category, reward,
                                                  new_state, header_parameter.initial_type_val)
            category_dict[header_parameter.name] = header_parameter.category
            val_dict[header_parameter.name] = header_parameter.val
            if header_parameter.category == 'request':
                header_parameter.request_table.learn(state, header_parameter.request_num, reward,
                                                     new_state, header_parameter.initial_request_val)
            if header_parameter.category == 'response':
                header_parameter.response_table.learn(state, header_parameter.response_num, reward,
                                                      new_state, header_parameter.initial_response_val)
        for body_parameter in delete_endpoint.body_parameters:
            if body_parameter.type == 'Bool':
                continue
            if body_parameter.name in PREDEFINED_DICT:
                continue
            if body_parameter.category == 'fixed':
                continue
            body_parameter.category_table.learn(state, body_parameter.category, reward,
                                                new_state, body_parameter.initial_type_val)
            category_dict[body_parameter.name] = body_parameter.category
            val_dict[body_parameter.name] = body_parameter.val
            if body_parameter.category == 'request':
                body_parameter.request_table.learn(state, body_parameter.request_num, reward,
                                                   new_state, body_parameter.initial_request_val)
            if body_parameter.category == 'response':
                body_parameter.response_table.learn(state, body_parameter.response_num, reward,
                                                    new_state, body_parameter.initial_response_val)

        if not flag or not check_response(response):
            if response == None:
                continue
            if flag and response.status_code >= 500:
                sequence_endpoint = Sequence_Endpoint(delete_endpoint.url, response.request.method,
                                                      response.request.url, dict(response.request.headers),
                                                      response.request.body.decode(
                                                          'utf-8') if response.request.body else None, category_dict,
                                                      val_dict)
                error_endpoints.append(sequence_endpoint)

            continue
        else:
            i = i + random.randint(1, 20)
            request_sequence.extend(temp_request_sequence)
            update_redis(delete_endpoint.url_parameters)
            update_redis(delete_endpoint.query_parameters)
            update_redis(delete_endpoint.header_parameters)
            update_redis(delete_endpoint.body_parameters)

            sequence_endpoint = Sequence_Endpoint(delete_endpoint.url, response.request.method, response.request.url,
                                                  dict(response.request.headers), response.request.body.decode(
                    'utf-8') if response.request.body else None, category_dict, val_dict)
            endpoint_sequence.append(sequence_endpoint)

        if response_text:
            if type(response_text) == dict:
                for name, val in response_text.items():
                    for response_parameter in delete_endpoint.response_parameters:
                        if response_parameter.name == name:
                            if len(str(val)) < 200:
                                response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val, name)
                                response_sequence.append(response_sequence_parameter)
            elif type(response_text) == list:
                for response_text_ in response_text:
                    try:
                        for name, val in response_text_.items():
                            for response_parameter in delete_endpoint.response_parameters:
                                if response_parameter.name == name:
                                    if len(str(val)) < 200:
                                        response_sequence_parameter = Sequence_Parmeter(response_parameter.num, val,
                                                                                        name)
                                        response_sequence.append(response_sequence_parameter)
                    except:
                        pass

    result_endpoint_sequence = endpoint_sequence_duplicate(endpoint_sequence)
    mongo_insert(mongo_conn, 'success', result_endpoint_sequence)

    return success_endpoints, error_endpoints
