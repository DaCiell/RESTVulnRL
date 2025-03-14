import time
import sys
import codecs
import glob
import json
import re
import string

import bson
import requests
import random
from pymongo import MongoClient

from cluster import cluster
from constraint import AUTH_LIST
from logger import *
from type import Sequence_Endpoint
from db import *
from config import *


def get_payload(dir, ip):
    txt_files = glob.glob(os.path.join(dir, '*.txt'))
    contents = []
    for file_path in txt_files:
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.readlines()
            contents.extend(file_content)
    contents.append(f"<img src='{ip}'>")
    return contents


def generate_ordered_random_string_from_list(strings):
    min_length = min(len(s) for s in strings)

    new_string = ''.join(random.choice([s[i] for s in strings]) for i in range(min_length))

    return new_string


def detect(base_url, validation_ip):
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_NAME]
    collection = db['success']
    documents = list(collection.find())
    payloads = get_payload('payload/fuzzdb/sql-injection', validation_ip)

    auths = []
    for doc in documents:
        endpoints = []
        for i in range(1, len(doc) - 1):
            endpoints.append(doc['endpoint' + str(i)])

        for endpoint in endpoints:
            if endpoint['val_dict']:
                val_dict = endpoint['val_dict']
                for key, value in val_dict.items():
                    if 'auth' in key.lower():
                        auths.append(value)
                    elif key.lower() in AUTH_LIST:
                        auths.append(value)
    auths = list(set(auths))
    for _ in range(10 * len(auths)):
        new_auth = generate_ordered_random_string_from_list(auths)
        auths.append(new_auth)

    document = documents[0]
    id = document['id']
    endpoints = []
    for i in range(1, len(document) - 1):
        endpoints.append(document['endpoint' + str(i)])
    mutate_endpoints = []

    for endpoint in endpoints:
        if endpoint['category_dict']:
            if 'register' in endpoint['path']:
                continue
            mutate_endpoints.append(endpoint)
    random_mutate = random.choice(mutate_endpoints)
    temp_endpoints = []
    for endpoint in endpoints:
        id = endpoint['id']
        path = endpoint['path']
        method = endpoint['method']
        url = endpoint['url']
        headers = endpoint['headers']
        body = endpoint['body']
        if body:
            body_json = json.loads(body)
        else:
            body_json = {}
        category_dict = endpoint['category_dict']
        val_dict = endpoint['val_dict']
        if 'register' in path:
            continue

        if id == random_mutate['id']:
            mutate_parameters = []
            for parameter, category in category_dict.items():
                mutate_parameters.append(parameter)
            k = random.randint(1, len(mutate_parameters))
            mutate_parameters_ = random.sample(mutate_parameters, k)
            responses = []
            for mutate_parameter in mutate_parameters_:
                if mutate_parameter in headers:
                    for auth in auths:
                        if auth != headers[mutate_parameter]:
                            headers[mutate_parameter] = auth
                else:
                    if type(body_json) == dict:
                        if mutate_parameter in body_json and 'url' in mutate_parameter.lower():
                            body_json[mutate_parameter] = validation_ip
                        else:
                            if random.choice([1, 2]) == 1:
                                payload = random.choice(payloads)
                            else:
                                if type(val_dict[mutate_parameter]) == int or type(
                                        val_dict[mutate_parameter] == bson.int64.Int64):
                                    payload = random.randint(1, 1000000000000)
                                elif type(val_dict[mutate_parameter]) == str:
                                    characters = string.ascii_letters + string.digits
                                    payload = ''.join(random.choice(characters) for _ in range(10))
                                elif type(val_dict[mutate_parameter]) == bool:
                                    payload = random.choice([True, False])
                            temp_url = url
                            matches = re.findall(r'\{([^}]+)\}', path)
                            if mutate_parameter in body_json:
                                if type(payload) == int or type(payload) == bool:
                                    body_json[mutate_parameter] = payload
                                else:
                                    body_json[mutate_parameter] = payload.strip()
                            elif matches:
                                for match in matches:
                                    if mutate_parameter == match:
                                        temp_url = base_url + path
                                        temp_url = temp_url.replace('{' + match + '}', str(payload))
                                        url = temp_url
                    else:
                        if mutate_parameter in body_json[0] and 'url' in mutate_parameter.lower():
                            body_json[0][mutate_parameter] = validation_ip
                        else:
                            if random.choice([1, 2]) == 1:
                                payload = random.choice(payloads)
                            else:
                                if type(val_dict[mutate_parameter]) == int or type(
                                        val_dict[mutate_parameter] == bson.int64.Int64):
                                    payload = random.randint(1, 1000000000000)
                                elif type(val_dict[mutate_parameter]) == str:
                                    characters = string.ascii_letters + string.digits
                                    payload = ''.join(random.choice(characters) for _ in range(10))
                                elif type(val_dict[mutate_parameter]) == bool:
                                    payload = random.choice([True, False])
                            temp_url = url
                            matches = re.findall(r'\{([^}]+)\}', path)
                            if mutate_parameter in body_json:
                                if type(payload) == int or type(payload) == bool:
                                    body_json[0][mutate_parameter] = payload
                                else:
                                    body_json[0][mutate_parameter] = payload.strip()
                            elif matches:
                                for match in matches:
                                    if mutate_parameter == match:
                                        temp_url = base_url + path
                                        temp_url = temp_url.replace('{' + match + '}', str(payload))
                                        url = temp_url
            if method == 'GET':
                response = requests.get(url=url, headers=headers)
                request_log(response)
            elif method == 'DELETE':
                response = requests.delete(url=url, headers=headers)
                request_log(response)
            elif method == 'POST':
                response = requests.post(url=url, headers=headers, json=body_json)
            else:
                response = requests.put(url=url, headers=headers, json=body_json)
            request_log(response)
            responses.append(response)
            indices = cluster(responses)
            for i in indices:
                if responses[i].status_code >= 200 and responses[i].status_code < 400:
                    for mutate_parameter in mutate_parameters_:
                        val_dict[mutate_parameter] = payloads[i]
                        sequence_endpoint = Sequence_Endpoint(path, method, responses[i].request.url,
                                                              dict(responses[i].headers),
                                                              responses[i].request.body.decode('utf-8') if responses[
                                                                  i].request.body else None, category_dict, val_dict)
                        temp_endpoints_copy = temp_endpoints.copy()
                        temp_endpoints_copy.append(sequence_endpoint)
                        mongo_insert(mongo_conn, 'exploit', temp_endpoints_copy)
        else:
            if method == 'GET':
                response = requests.get(url=url, headers=headers)
                request_log(response)
            elif method == 'DELETE':
                response = requests.delete(url=url, headers=headers)
                request_log(response)
            elif method == 'POST':
                response = requests.post(url=url, headers=headers, json=body_json)
            else:
                response = requests.put(url=url, headers=headers, json=body_json)
            request_log(response)
            sequence_endpoint = Sequence_Endpoint(path, method, url, headers, body, category_dict, val_dict)
            temp_endpoints.append(sequence_endpoint)

    client.close()


def main():
    if len(sys.argv) != 3:
        print("Usage: python detect.py <base_url> <validation_ip>")
        sys.exit(1)

    base_url = sys.argv[1]
    validation_ip = sys.argv[2]

    detect(base_url, validation_ip)


if __name__ == "__main__":
    main()
