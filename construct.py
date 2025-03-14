import time
import sys

from process import *
from request.request import *


def main(json_file, yaml_file, url):
    # Process the input files
    endpoints, request_parameters = process_json(json_file)
    endpoints, response_parameters = process_response(yaml_file, endpoints)

    logger.info(f'Endpoints length: {str(len(endpoints))}')

    temp_endpoints_ = []
    for endpoint in endpoints:
        temp_endpoints_.append(endpoint.method + ' ' + endpoint.url)

    run_duration = 7200
    start_time = time.time()
    success_endpoints = []
    error_endpoints = []
    temp_error_endpoints = []

    while True:
        # Perform the request sequence with the provided URL
        temp_endpoints, temp_endpoints2 = request_sequence(url, endpoints)
        success_endpoints = list(set(success_endpoints) | set(temp_endpoints))

        for temp_endpoint in temp_endpoints2:
            if not any(error_endpoint.path == temp_endpoint.path and error_endpoint.method == temp_endpoint.method for
                       error_endpoint in error_endpoints):
                error_endpoints.append(temp_endpoint)
                temp_error_endpoints.append(temp_endpoint.method + ' ' + temp_endpoint.path)

        fail_endpoints = [item for item in temp_endpoints_ if item not in success_endpoints]

        logger.warning(f'Success endpoints: {success_endpoints}')
        logger.warning(f'Success endpoints length: {str(len(success_endpoints))}')
        logger.warning(f'Fail endpoints: {fail_endpoints}')
        logger.warning(f'Fail endpoints length: {str(len(fail_endpoints))}')
        logger.warning(f'Error endpoints: {temp_error_endpoints}')
        logger.warning(f'Error endpoints length: {str(len(temp_error_endpoints))}')

        if time.time() - start_time > run_duration:
            mongo_insert(mongo_conn, 'error', error_endpoints)
            break


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python construct.py <json_file> <yaml_file> <url>")
        sys.exit(1)

    json_file = sys.argv[1]
    yaml_file = sys.argv[2]
    url = sys.argv[3]

    main(json_file, yaml_file, url)
