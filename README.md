# hv-controls
Simple GUI for HV source controls

## Installation

Run `pip install -e .` or install dependencies manualy:
```
pip install pyqt pylibftdi ftd2xx
```
Also driver FTDI or FTD2XX must be installed in OS.

## For developers

Файл `hv_device.py` содержит класс `HVDevice`, который принимает команды от консольного или графического интерфейса и превращает их в команды для низкоуровневых драйверов. Файлы `ftdi_device.py` и `ftd2xx_device.py` содержать классы-обертки над драйверами STDI и STD2XX (для него пока только заглушка).

Файл `cmd_ui.py` предоставляет консольный интерфейс для управления прибором, будет полезен при отладке.
Файл `qt_ui.py` предоставляет графический интерфейс для управления прибором.
Файл `run.py` содержит точки входа, для запуска которых `pip` умеет создавать shell и bat скрипты.
Файл `main.py` позволяет запускать консольный и графический интерфейс

В директории `hv/device_data` хранится информация об источниках различных серий, источник должен сообщать свою серию, и оттуда буду браться данные.