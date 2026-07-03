import hashlib
import json
import os
import shutil
import time
from datetime import datetime
from datetime import timedelta
from functools import reduce
from pathlib import Path

import yaml
from openai import OpenAI

from request_generator.prompting import create_prompt, call_openai

today_date = datetime.today().strftime("%Y-%m-%d")
start_time = time.time()

client = OpenAI()
DOMAINS = {'insurance', 'ecommerce'}
NUM_REQUESTS = 10


def convert_request_to_yaml(entry):
    return {
        "dataUsageAgreementSpecification": "0.0.1",
        "id": hashlib.sha256(str(entry.get("purpose", "")).encode()).hexdigest(),
        "info": {
            "purpose": entry.get("purpose", ""),
            "status": "requested",
            "active": False,
            "startDate": today_date
        },
        "provider": {
            "dataProductId": entry.get("provider", {}).get("dataProductId", ""),
            "outputPortId": entry.get("provider", {}).get("outputPortId", "")
        },
        "consumer": {
            "teamId": entry.get("consumer", {}).get("teamId", ""),
            "dataProductId": generate_dataapplication_id(entry),
        },
        "tags": [],
        "links": {},
        "custom": {}
    }


def create_dataproduct(entry):
    return {
        "dataProductSpecification": "0.0.1",
        "id": generate_dataapplication_id(entry),
        "info": {
            "title": entry.get("consumer", {}).get("data_application_name", ""),
            "owner": entry.get("consumer", {}).get("teamId", ""),
            "description": entry.get("consumer", {}).get("data_application_description", "")
        },
        "tags": [],
        "links": {},
        "custom": {},
        "inputPorts": [],
        'assets': []
    }


def generate_dataapplication_id(entry):
    return hashlib.sha256(str(entry.get("consumer", {}).get("data_application_name", "")).encode()).hexdigest()


def copy_base_data_map(src_dir, dest_dir):
    # Ensure destination directory exists
    # Loop through files in source directory
    for file_name in os.listdir(src_dir):
        if file_name.endswith(".yaml") or file_name.endswith(".yml"):
            src_path = os.path.join(src_dir, file_name)
            dest_path = os.path.join(dest_dir, file_name)
            shutil.copy2(src_path, dest_path)


def create_access_request_testsuite(domain, json_data, provider):
    generated_requests = []
    for request in json_data['requests']:
        dataproduct = create_dataproduct(request)
        yaml_dataproduct = yaml.dump(dataproduct, default_flow_style=False)

        converted_request = convert_request_to_yaml(request)
        request_yaml = yaml.dump(converted_request, default_flow_style=False)

        basedir_test = f"test_executor/testcases/{domain}/{converted_request['id']}"
        Path(basedir_test).mkdir(parents=True, exist_ok=True)

        # Save YAML output to file
        with open(f"{basedir_test}/access_requests_{converted_request['id']}.yaml", "w") as file:
            file.write(request_yaml)
        with open(f"{basedir_test}/data_products_{dataproduct['id']}.yaml", "w") as file:
            file.write(yaml_dataproduct)

        copy_base_data_map(f"test_executor/accesskoala-{domain}", basedir_test)
        # Print the formatted YAML
        print(request_yaml)
        consumer = request.get("consumer", {})
        generated_requests.append({
            "organization": f"accesskoala-{domain}-test",
            "name": request.get("title", ""),
            "purpose": request.get("purpose", ""),
            "consumer_team": consumer.get("teamId", ""),
            "consumer_name": consumer.get("data_application_name", ""),
            "consumer_description": consumer.get("data_application_description", ""),
            "provider": provider,
            "baseDir": basedir_test.replace("test_executor/", ""),
            "accessRequest": converted_request['id'],
            "expected": request.get("expected_decision", None)
        })
    return generated_requests


class DataMap:
    def __init__(self):
        self.data_contracts = list()
        self.data_products = list()
        self.teams = list()

    def __str__(self):
        return reduce(lambda a, b: f"{a}\n{b}", (map(lambda elem: f"{str(elem)}", self.data_contracts + self.data_products + self.teams)))


def read_datamap(datamap_folder):
    data_map = DataMap()
    for file in os.listdir(datamap_folder):
        if file.endswith(".yaml") or file.endswith(".yml"):
            file_path = os.path.join(datamap_folder, file)
            if file.startswith("data_contracts_"):
                content = read_datamesh(file_path)
                data_map.data_contracts.append(content)
            if file.startswith("data_products_"):
                content = read_datamesh(file_path)
                data_map.data_products.append(content)
            if file.startswith("teams_"):
                content = read_datamesh(file_path)
                data_map.teams.append(content)

    return data_map


def read_datamesh(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        return yaml.load(content, Loader=yaml.FullLoader)


def read_policy_text(domain):
    with open(f"test_executor/accesskoala-{domain}/policy.txt", 'r', encoding='utf-8') as policy_doc:
        return policy_doc.read()


num_requests = 0
for domain in DOMAINS:
    policy = read_policy_text(domain)
    generated_requests = []
    datamap = read_datamap(f"test_executor/accesskoala-{domain}")
    shutil.rmtree(f"test_executor/testcases/{domain}", ignore_errors=True)
    for producer in datamap.data_products:
        for output_port in producer['outputPorts']:
            messages = create_prompt(domain, datamap, producer, list(filter(lambda dc: dc['id'] == output_port['dataContractId'], datamap.data_contracts)).pop(), NUM_REQUESTS, policy)
            print(f"{domain}--{producer['info']['title']}--{output_port['dataContractId']}\n{messages[1]['content']}")
            raw_access_request = call_openai(client, messages)
            with open(f"request_generator/raw_jsons/{domain}/{producer['info']['title']}_{output_port['dataContractId']}.json", "w") as file:
                file.write(raw_access_request)
            for request_yaml in create_access_request_testsuite(domain, json.loads(raw_access_request), f"{producer['info']['title']}/{output_port['dataContractId']}"):
                generated_requests.append(request_yaml)

    with open(f"test_executor/master-table.{domain}.gen.json", "w") as file:
        json.dump(generated_requests, file)
    num_requests += len(generated_requests)

print(f"Generated {num_requests} requests in {timedelta(seconds=time.time() - start_time)}.")
