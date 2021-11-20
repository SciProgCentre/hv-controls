# hv-controls
Simple GUI for HV source controls.

Can be used for [Mantigora](http://mantigora.ru/highvolt_HV.htm) devices.

Tested on Ubuntu 21.10 with HT-60-30-P. Proposal correct work on all platform for HT-60-*, HT-15-*, HT2000, HV2000, HV6000.

## Installation

1. Install USB/FTDI drivers. Application used different drivers for Linux and Windows. For Linux used `pyftdi` with `libusb` (On Debian/Ubuntu use `sudo apt-get install libusb-1.0`) .For Windows used FTD2XX.
2. Configure our system what would to allow using drivers from user-space. For linux see [here](https://eblot.github.io/pyftdi/installation.html#debian-ubuntu-linux) or run application with `sudo`.
3. Install application from source, move apllication source directory and run `pip install -e .` (Also you can install dependencies manualy `pip install pyqt5 pyftdi ftd2xx`)
4. Run `hv-controls` in terminal (or `python3 main.py`). Use option `--no-gui` for run console apps. Use options `--debug` for getting debug information in log. 

## For developers

### Devices parameters

Devices parameters located in `hv/device_data` and based on file `Unit1.pas`, inforamtion from vendor and specification of protocol. 

Parameters of next devices isn't consistent:

* *HT-15-10-P* and *HT-15-10-N*: max current 3000 mcA or 750 mcA?
* _HT-6-*_ absent current step.
* *HT4000*, *HT6000*, _HR*_ absent codemax ADC and DAC.

### Code overview
Файл `hv_device.py` содержит класс `HVDevice`, который принимает команды от консольного или графического интерфейса и превращает их в команды для низкоуровневых драйверов. Файлы `ftdi_device.py` и `ftd2xx_device.py` содержать классы-обертки над драйверами STDI и STD2XX (для него пока только заглушка).

Файл `cmd_ui.py` предоставляет консольный интерфейс для управления прибором, будет полезен при отладке.
Файл `qt_ui.py` предоставляет графический интерфейс для управления прибором.
Файл `run.py` содержит точки входа, для запуска которых `pip` умеет создавать shell и bat скрипты.
Файл `main.py` позволяет запускать консольный и графический интерфейс

В директории `hv/device_data` хранится информация об источниках различных серий, источник должен сообщать свою серию, и оттуда буду браться данные.
