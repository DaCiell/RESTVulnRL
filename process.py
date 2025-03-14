import json
import re

import yaml
from type import Request_Parameter, Endpoint, Response_Parameter


def process_json(file):
    with open(file, 'r', encoding='utf-8') as file:
        grammar_json = json.load(file)
    requests = grammar_json['Requests']
    endpoints = []
    index = 0
    request_parameter_list = []
    for request in requests:
        id = request['id']
        url = id['endpoint']
        if not url:
            url = "/"
        method = request['method'].lower()

        if url == '/Repositories' and method == 'post':
            pass

        url_parameter_list = []
        if '{' in url and '}' in url:
            matches = re.findall(r'\{([^}]+)\}', url)
            for match in matches:
                index = index + 1
                name = match
                type = 'string'
                example = ''
                required = True
                readonly = False
                enum = []
                temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                url_parameter_list.append(temp_parameter)
                request_parameter_list.append(temp_parameter)

        query_parameter = request['queryParameters'][0][1]
        parameter_list = query_parameter['ParameterList']
        query_parameter_list = []
        for parameter in parameter_list:
            name = parameter['name']
            if parameter['payload'].get('InternalNode'):
                payload = parameter['payload']['InternalNode'][1]
                for payload_item in payload:
                    if payload_item.get('LeafNode'):
                        payload_node = payload_item['LeafNode']
                        if payload_node.get('payload').get('Fuzzable'):
                            type = payload_node.get('payload').get('Fuzzable').get('primitiveType')
                            example = payload_node.get('payload').get('Fuzzable').get('exampleValue', '')
                        else:
                            type = payload_node.get('payload').get('DynamicObject').get('primitiveType')
                            example = payload_node.get('payload').get('DynamicObject').get('exampleValue', '')
                        required = payload_node['isRequired']
                        readonly = payload_node['isReadOnly']
                        if not required:
                            continue
                        index = index + 1
                        enum = []
                        temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                        query_parameter_list.append(temp_parameter)
                        request_parameter_list.append(temp_parameter)


            elif parameter['payload'].get('LeafNode'):
                payload_node = parameter['payload']['LeafNode']
                if payload_node.get('payload').get('Fuzzable'):
                    type = payload_node.get('payload').get('Fuzzable').get('primitiveType')
                    example = payload_node.get('payload').get('Fuzzable').get('exampleValue', '')
                else:
                    type = payload_node.get('payload').get('DynamicObject').get('primitiveType')
                    example = payload_node.get('payload').get('DynamicObject').get('exampleValue', '')
                required = payload_node['isRequired']
                readonly = payload_node['isReadOnly']
                if not required:
                    continue
                index = index + 1
                enum = []
                temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                query_parameter_list.append(temp_parameter)
                request_parameter_list.append(temp_parameter)

        body_parameter = request['bodyParameters'][0][1]
        parameter_list = body_parameter['ParameterList']
        body_parameter_list = []
        body_type = 'object'
        for parameter in parameter_list:
            if parameter['payload'].get('InternalNode'):
                property_type = parameter['payload']['InternalNode'][0].get('propertyType', 'object').lower()
                if property_type == 'array':
                    body_type = 'array'
                else:
                    body_type = 'object'
                payload = parameter['payload']['InternalNode'][1]
                for payload_item in payload:
                    if payload_item.get('InternalNode'):
                        payload_ = payload_item['InternalNode'][1]
                        for payload_item_ in payload_:
                            if payload_item_.get('LeafNode'):
                                payload_node_ = payload_item_['LeafNode']
                                name = payload_node_['name']
                                if not name:
                                    continue
                                if payload_node_.get('payload').get('Fuzzable'):
                                    type = payload_node_.get('payload').get('Fuzzable').get('primitiveType')
                                    example = payload_node_.get('payload').get('Fuzzable').get('exampleValue', '')
                                else:
                                    type = payload_node_.get('payload').get('DynamicObject').get('primitiveType')
                                    example = payload_node_.get('payload').get('DynamicObject').get('exampleValue', '')
                                required = payload_node_['isRequired']
                                readonly = payload_node_['isReadOnly']
                                if not required:
                                    continue
                                index = index + 1
                                enum = []
                                temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                                body_parameter_list.append(temp_parameter)
                                request_parameter_list.append(temp_parameter)
                            if payload_item_.get('InternalNode'):
                                payload_node = payload_item['InternalNode'][0]
                                name = payload_node['name']
                                if not name:
                                    continue
                                type = payload_node['propertyType']
                                index = index + 1
                                enum = []
                                example = '{}'
                                required = True
                                readonly = False
                                temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                                body_parameter_list.append(temp_parameter)
                                request_parameter_list.append(temp_parameter)
                    if payload_item.get('LeafNode'):
                        payload_node = payload_item['LeafNode']
                        name = payload_node['name']
                        if not name:
                            continue
                        if payload_node.get('payload').get('Fuzzable'):
                            type = payload_node.get('payload').get('Fuzzable').get('primitiveType')
                            example = payload_node.get('payload').get('Fuzzable').get('exampleValue', '')
                        else:
                            type = payload_node.get('payload').get('DynamicObject').get('primitiveType')
                            example = payload_node.get('payload').get('DynamicObject').get('exampleValue', '')
                        required = payload_node['isRequired']
                        readonly = payload_node['isReadOnly']
                        if not required:
                            continue
                        index = index + 1
                        enum = []
                        temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                        body_parameter_list.append(temp_parameter)
                        request_parameter_list.append(temp_parameter)
                    if payload_item.get('InternalNode'):
                        payload_node = payload_item['InternalNode'][0]
                        name = payload_node['name']
                        if not name:
                            continue
                        type = payload_node['propertyType']
                        index = index + 1
                        enum = []
                        example = '{}'
                        required = True
                        readonly = False
                        temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                        body_parameter_list.append(temp_parameter)
                        request_parameter_list.append(temp_parameter)
            elif parameter['payload'].get('LeafNode'):
                payload_node = parameter['payload']['LeafNode']
                name = payload_node['name']
                if payload_node.get('payload').get('Fuzzable'):
                    type = payload_node.get('payload').get('Fuzzable').get('primitiveType')
                    example = payload_node.get('payload').get('Fuzzable').get('exampleValue', '')
                else:
                    type = payload_node.get('payload').get('DynamicObject').get('primitiveType')
                    example = payload_node.get('payload').get('DynamicObject').get('exampleValue', '')
                required = payload_node['isRequired']
                readonly = payload_node['isReadOnly']
                if not required:
                    continue
                index = index + 1
                enum = []
                temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
                body_parameter_list.append(temp_parameter)
                request_parameter_list.append(temp_parameter)

        header_parameter = request['headerParameters'][0][1]
        parameter_list = header_parameter['ParameterList']
        header_parameter_list = []
        for parameter in parameter_list:
            name = parameter['name']
            type = parameter.get('payload').get('LeafNode').get('payload').get('Fuzzable').get('primitiveType')
            example = parameter.get('payload').get('LeafNode').get('payload').get('Fuzzable').get('exampleValue',
                                                                                                  '')
            required = parameter.get('payload').get('LeafNode').get('isRequired')
            readonly = parameter.get('payload').get('LeafNode').get('isReadOnly')
            if not required:
                continue
            index = index + 1
            enum = []
            temp_parameter = Request_Parameter(index, name, type, example, required, readonly, enum)
            header_parameter_list.append(temp_parameter)
            request_parameter_list.append(temp_parameter)
        endpoint = Endpoint(url, method, url_parameter_list, query_parameter_list, body_parameter_list,
                            header_parameter_list, body_type)
        endpoints.append(endpoint)

    for endpoint in endpoints:
        for url_parameter in endpoint.url_parameters:
            url_parameter.init_request_table(index)
        for query_parameter in endpoint.query_parameters:
            query_parameter.init_request_table(index)
        for body_parameter in endpoint.body_parameters:
            body_parameter.init_request_table(index)
        for header_parameter in endpoint.header_parameters:
            header_parameter.init_request_table(index)

    return endpoints, request_parameter_list


def process_response(file, endpoints):
    with open(file, 'r', encoding='utf-8') as file:
        spec_yaml = yaml.safe_load(file)
    paths = spec_yaml['paths']
    index = 0
    endpoints_ = []
    response_parameter_list = []
    for path_name, path in paths.items():
        for method_name, method in path.items():
            for endpoint in endpoints:
                if endpoint.url == path_name and endpoint.method == method_name:
                    endpoint_ = endpoint
                    break
            flag = False
            if not isinstance(method, dict):
                break
            if method.get('requestBody'):
                content = method['requestBody']['content']
                if content.get('multipart/form-data'):
                    schema = content['multipart/form-data']['schema']
                    properties = schema.get('properties')
                    for property_name, property_content in properties.items():
                        name = property_name
                        type = 'file'
                        example = ''
                        required = True
                        readonly = False
                        enum = []

                        body_parameter = Request_Parameter(1000, name, type, example, required, readonly, enum)
                        endpoint.info()
                        body_parameter.request_table = endpoint_.header_parameters[0].request_table
                        endpoint_.body_parameters.append(body_parameter)
                        flag = True
                try:
                    endpoints_.append(endpoint_)
                except:
                    pass

            if method.get('parameters'):
                parameters = method['parameters']
                for par in parameters:
                    if par.get('schema'):
                        schema = par['schema']
                        if 'enum' in schema:
                            for url_parameter in endpoint_.url_parameters:
                                if url_parameter.name == par['name']:
                                    url_parameter.enum = schema['enum']
                            for query_parameter in endpoint_.query_parameters:
                                if query_parameter.name == par['name']:
                                    query_parameter.enum = schema['enum']
                            for body_parameter in endpoint_.body_parameters:
                                if body_parameter.name == par['name']:
                                    body_parameter.enum = schema['enum']
                            for header_parameter in endpoint_.header_parameters:
                                if header_parameter.name == par['name']:
                                    header_parameter.enum = schema['enum']

            if method.get('responses'):
                response_parameters = []
                for status_code, response in method['responses'].items():
                    if response.get('content'):
                        for content_type, content in response['content'].items():
                            if content['schema'].get('type') == 'object':
                                properties = content['schema'].get('properties')
                            elif content['schema'].get('type') == 'array':
                                properties = content['schema'].get('items').get('properties')
                            else:
                                break
                            if not properties:
                                break
                            for property_name, property_content in properties.items():
                                try:
                                    type = property_content['type']
                                    example = property_content.get('example', '')
                                    enum = property_content.get('enum', [])
                                    index = index + 1
                                    parameter = Response_Parameter(index, property_name, type, example, enum,
                                                                   int(status_code))
                                    response_parameters.append(parameter)
                                    response_parameter_list.append(parameter)
                                except:
                                    pass
                try:
                    endpoint_.response_parameters = response_parameters
                    flag = True
                except:
                    pass

            if flag:
                endpoints_.append(endpoint_)
    for endpoint in endpoints_:
        for url_parameter in endpoint.url_parameters:
            url_parameter.init_response_table(index)
        for query_parameter in endpoint.query_parameters:
            query_parameter.init_response_table(index)
        for body_parameter in endpoint.body_parameters:
            body_parameter.init_response_table(index)
        for header_parameter in endpoint.header_parameters:
            header_parameter.init_response_table(index)
    return endpoints_, response_parameter_list
