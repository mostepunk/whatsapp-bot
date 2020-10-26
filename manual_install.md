# WhatsApp Bot

## Источники
- [Yowsup](https://github.com/tgalal/yowsup)
- [Мануал по настройке](https://iamjagjeetubhi.wordpress.com/2017/09/21/how-to-use-yowsup-the-python-whatsapp-library-in-ubuntu/)


## Процесс установки:

### Подготовить все компоненты

    ```bash
    sudo apt-get install python-dateutil
    sudo apt-get install python-setuptools
    sudo apt-get install python-dev
    sudo apt-get install libevent-dev
    sudo apt-get install ncurses-dev
    ```
### Скачать репозиторий 

    ```bash
    git clone git://github.com/tgalal/yowsup.git
    ```
### Внести правки в [этих файлах](https://github.com/tgalal/yowsup/pull/2924/files/b0b80e1dbbb0103d7e990f2b68660addb46a942f). Проблема в обновлении декодирования
### Установить библиотеку
    ```bash
    sudo python3 setup.py install
    ```
### Регистрация приложения
- Создать файл `dexMD5.py`
- Вставить код из [этого файла](https://github.com/mgp25/classesMD5-64/blob/master/dexMD5.py)
- Сохранить и выйти
- Скачать последнюю версию приложения с сайта [Whatsapp](https://www.whatsapp.com/android/) в текущую папку
- `pip3 install pyaxmlparser`
- `python3 dexMD5.py WhatsApp.apk`
- Нам нужно будет от туда следующее:
    ```bash
    Version: 2.20.178
    ClassesDex: j+Q00eJqFSydkEW2hUSbTg==
    ```
- Записать эти данные в `yowsup/env/env_android.py` в переменные:
    - `_MD5_CLASSES`
    - `_VERSION`
- `sudo python3 setup.py build`
- `sudo python3 setup.py install`

### Авторизация:
- Сначала установить симку в телефон
- Зарегистрироваться,  отослать несколько сообщений кому-то в чатик и получить ответы.
- Потом пройти регистрацию в программе `yowsup`
    - `python3 yowsup-cli registration --requestcode sms --phone 7xxxxxxxxxx --cc 7 --mcc 250 --mnc 01 -E android`
        > Может ругаться на отсутствие прав доступа, можно вначале ввести `sudo`\
        >  `--requestcode` или `-r` - Подтверждение номера телефона по смс(`sms`) или звонок (`voice`)\
        >  `--phone` номер телефона без `+` начиная с 7\
        >  `--cc` country code код страны для РФ это 7\
        >  `--mcc`- mobile country code — это другой код страны (для России это 250)\
        >  `--mnc` mobile network code — это код вашего оператора. (01 — МТС, 02 — мегафон, 20 — теле2, 99 — билайн)
    - Дождаться смс с кодом или звонка, подставляем код на место `ххх-ххх`
    - `python3 yowsup-cli registration --register xxx-xxx --phone 7xxxxxxxxxx --cc 7 -E android`
        > Может ругаться на отсутствие прав доступа, можно вначале ввести `sudo`
    - Если все пройдет успешно, то придет такое сообщение в баше
        ```bash
        {
            "__version__": 1,
            "cc": "91",
            "client_static_keypair": "4LwtAptoy3o7RvZKi4/8**************+8O/1YzTqcWU78M/DK1cDap104G243EkySxN7eQ==",
            "expid": "qsufBg*******GpQV8zNTFg==",
            "fdid": "6a92d996-0c31-****-8bc1-6c8e12990dc8",
            "id": "Sow6yYuOVyGQ******vjVhwiMds=",
            "login": "7**********",
            "mcc": "250",
            "mnc": "01",
            "phone": "7**********",
            "sim_mcc": "000",
            "sim_mnc": "000"
        }
        ```
    - Сохраняем это дело в `config.json`
### Запуск приложения из консоли
- `yowsup-cli demos --yowsup --config config.json`
- Мы зашли в скрипт юсупа и сначала надо подключиться, выполнив команду `/L`, а потом можно слать сообщения
- `/message send 7xxxxxxx "Hello World!`
- Либо просто отправить команду из  консоли
    ```bash
    yowsup-cli demos -c config.json -s 7xxxxxxx "alarm"
    ```
