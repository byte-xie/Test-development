import pytest
import requests
import yaml
from tests.config import BASE_URL
import os
import logging


def get_token():
    url = f"{BASE_URL}/api/v1/login/access-token"
    data = {
        "username": "xiehaoliang@ks.com",
        "password": "xiehaoliang"
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token", "")


def load_test_data():
    # 获取项目根目录（case_FastApi）
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'token_validity.yaml')
    with open(data_path, encoding='utf-8') as f:
        return yaml.safe_load(f)


test_data = load_test_data()


@pytest.mark.parametrize("case", test_data)
def test_token_validity(case):
    if case["token_type"] == "valid":
        token = get_token()
    elif case["token_type"] == "invalid":
        token = "invalidtoken"
    else:
        token = ""
    url = f"{BASE_URL}/api/v1/login/test-token"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.post(url, headers=headers)
    log_msg = f"token_validity: token_type={case['token_type']}, status={response.status_code}, body={response.text}"
    print(log_msg)
    logging.info(log_msg)
    assert response.status_code == case["expected_status"]


if __name__ == "__main__":
    for case in test_data:
        try:
            test_token_validity(case)
            print(f"[PASS] token_type={case['token_type']}")
        except AssertionError as e:
            print(f"[FAIL] token_type={case['token_type']} -> {e}")
