import pytest
import requests
import yaml
from tests.config import BASE_URL
import os
import logging

def load_test_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'user_list.yaml')
    with open(data_path, encoding='utf-8') as f:
        return yaml.safe_load(f)

test_data = load_test_data()

SUPER_USER = {"username": "admin@example.com", "password": "xiehaoliang"}
NORMAL_USER = {"username": "normal@ks.com", "password": "normalpwd"}

def get_token(user_type):
    url = f"{BASE_URL}/api/v1/login/access-token"
    data = SUPER_USER if user_type == "super" else NORMAL_USER
    response = requests.post(url, data=data)
    return response.json().get("access_token", "")

@pytest.mark.parametrize("case", test_data)
def test_user_list(case):
    token = get_token(case["user_type"])
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/v1/users/"
    response = requests.get(url, headers=headers, params=case["params"])
    log_msg = f"user_list: case_type={case['case_type']}, params={case['params']}, status={response.status_code}, body={response.text}"
    print(log_msg)
    logging.info(log_msg)
    assert response.status_code == case["expected_status"]
    if case["expected_in_json"]:
        assert case["expected_in_json"] in response.text 