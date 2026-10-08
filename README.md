# Лабораторная работа №5: Автотесты для API (Redfish) с использованием PyTest

Автоматизированные тесты для проверки функционала Redfish REST API в OpenBMC.

## Покрытие тестами
* `test_authentication` — Авторизация в Redfish API и получение X-Auth-Token.
* `test_system_info` — Получение статуса системы и состояния питания (PowerState).
* `test_power_control` — Выполнение команды включения/сброса питания через Actions.
* `test_cpu_temperature_norm` — Запрос параметров температурных датчиков CPU.
* `test_cpu_sensors_redfish_ipmi` — Валидация списка сенсоров оборудования.

## Запуск
```bash
python3 -m venv venv
source venv/bin/activate
pip install pytest requests urllib3
pytest test_redfish.py -v