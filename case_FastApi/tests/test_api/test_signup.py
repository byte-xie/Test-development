import pytest
import requests
import yaml
from tests.config import BASE_URL
import os
import time
import random
import logging

def load_test_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'signup.yaml')
    with open(data_path, encoding='utf-8') as f:
        return yaml.safe_load(f)

test_data = load_test_data()

def gen_unique_email():
    return f"newuser_{int(time.time())}_{random.randint(1000,9999)}@ks.com"

@pytest.fixture(scope="module")
def repeat_email():
    return gen_unique_email()

@pytest.mark.parametrize("case", test_data)
def test_signup(case, repeat_email):
    url = f"{BASE_URL}/api/v1/users/signup"
    email = case["email"]
    if email == "{unique}":
        email = gen_unique_email()
    elif email == "{unique_repeat}":
        email = repeat_email
    payload = {
        "email": email,
        "password": case["password"]
    }
    if case["full_name"]:
        payload["full_name"] = case["full_name"]
    response = requests.post(url, json=payload)
    log_msg = f"signup: case_type={case['case_type']}, email={email}, status={response.status_code}, body={response.text}"
    print(log_msg)
    logging.info(log_msg)
    assert response.status_code == case["expected_status"]
    if case["expected_in_json"]:
        assert case["expected_in_json"] in response.json() 