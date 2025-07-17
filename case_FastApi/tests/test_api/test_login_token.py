import pytest
import requests
import yaml
from tests.config import BASE_URL
import os
import logging


def load_test_data():
    # 获取项目根目录（case_FastApi）
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'login_token.yaml')
    with open(data_path, encoding='utf-8') as f:
        return yaml.safe_load(f)


test_data = load_test_data()


@pytest.mark.parametrize("case", test_data)
def test_login_get_token(case):
    url = f"{BASE_URL}/api/v1/login/access-token"
    data = {
        "username": case["username"],
        "password": case["password"]
    }
    response = requests.post(url, data=data)
    log_msg = f"login_token: username={case['username']}, status={response.status_code}, body={response.text}"
    print(log_msg)
    logging.info(log_msg)
    assert response.status_code == case["expected_status"]
    if case["expected_in_json"]:
        assert case["expected_in_json"] in response.json()


if __name__ == "__main__":
    for case in test_data:
        try:
            test_login_get_token(case)
            print(f"[PASS] {case['username']} / {case['password']}")
        except AssertionError as e:
            print(f"[FAIL] {case['username']} / {case['password']} -> {e}")
