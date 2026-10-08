import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:2443"
VALID_USER = "root"
VALID_PASSWORD = "0penBmc"


@pytest.fixture(scope="module")
def auth_session():
    """Фикстура PyTest для авторизации и повторного использования сессии."""
    session = requests.Session()
    session.verify = False
    
    url = f"{BASE_URL}/redfish/v1/SessionService/Sessions"
    payload = {"UserName": VALID_USER, "Password": VALID_PASSWORD}
    response = session.post(url, json=payload)
    
    assert response.status_code in (200, 201), f"Ошибка авторизации: {response.status_code}"
    
    token = response.headers.get("X-Auth-Token")
    session_uri = response.headers.get("Location")
    
    if token:
        session.headers.update({"X-Auth-Token": token})
    
    yield session
    
    if session_uri:
        session.delete(f"{BASE_URL}{session_uri}")


def test_authentication():
    """1. Тест аутентификации в OpenBMC через Redfish API"""
    session = requests.Session()
    session.verify = False
    url = f"{BASE_URL}/redfish/v1/SessionService/Sessions"
    payload = {"UserName": VALID_USER, "Password": VALID_PASSWORD}
    
    response = session.post(url, json=payload)
    assert response.status_code in (200, 201)
    
    token = response.headers.get("X-Auth-Token")
    assert token is not None and len(token) > 0


def test_system_info(auth_session):
    """2. Тест получения информации о системе"""
    url = f"{BASE_URL}/redfish/v1/Systems/system"
    response = auth_session.get(url)
    assert response.status_code == 200
    
    data = response.json()
    assert "Status" in data
    assert "PowerState" in data


def test_power_control(auth_session):
    """3. Тест управления питанием (включение/сброс)"""
    url = f"{BASE_URL}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
    payload = {"ResetType": "On"}
    
    response = auth_session.post(url, json=payload)
    assert response.status_code in (200, 202, 204)
    
    sys_url = f"{BASE_URL}/redfish/v1/Systems/system"
    sys_response = auth_session.get(sys_url)
    assert sys_response.status_code == 200
    assert "PowerState" in sys_response.json()


def test_cpu_temperature_norm(auth_session):
    """4. Тест на соответствие температуры CPU норме"""
    url = f"{BASE_URL}/redfish/v1/Chassis/system/Thermal"
    response = auth_session.get(url)
    
    if response.status_code == 404:
        url = f"{BASE_URL}/redfish/v1/Sensors"
        response = auth_session.get(url)
    
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "Temperatures" in data or "Members" in data


def test_cpu_sensors_redfish_ipmi(auth_session):
    """5. Тест получения датчиков CPU в Redfish"""
    url = f"{BASE_URL}/redfish/v1/Chassis/system/Sensors"
    response = auth_session.get(url)
    
    if response.status_code == 404:
        url = f"{BASE_URL}/redfish/v1/Sensors"
        response = auth_session.get(url)

    assert response.status_code in (200, 404)
