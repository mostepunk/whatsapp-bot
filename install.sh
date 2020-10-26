#!/bin/bash
GREEN='\033[0;32m'      #  ${GREEN}
NORMAL='\033[0m'      #  ${NORMAL}
YELLOW='\033[0;33m'     #  ${YELLOW}

timer_func() {
    while sleep 0.03; do echo -ne "${YELLOW}#${NORMAL}" >&2; done
}

run_bot()
{
	cat /usr/src/wabot/label.txt
    cd /usr/src/wabot/yowsup
    echo === $phone_number ===
	python3 run.py 
}

register_bot()
{
	cd /usr/src/wabot/yowsup
	# отправляется запрос на сервер wa для регистрации нового устройства для симки
	python3 yowsup-cli registration --requestcode $answer_type --phone $phone_number --cc 7 --mcc 250 --mnc $operator_code -E android

	echo Введите полученный код в формате xxx-xxx
	read sms_answer

	# регистрируем
	python3 yowsup-cli registration --register $sms_answer --phone $phone_number --cc 7 -E android
}

install()
{
    echo -e "${GREEN}Installing yowsup...${NORMAL}"

    timer_func &
    timer_func_pid=$!

    cat pkg/listip.txt >> /etc/hosts
	cp -r pkg/yowsup/ .
	cp pkg/dexMD5.py .
	cp pkg/WhatsApp.apk .
    cp -r script/* yowsup/

	cd yowsup
	python3 setup.py install &>/dev/null
	cd ..

	# парсит установочный пакет с сайта https://www.whatsapp.com/android/ 
	# Извлекает от туда хэш сумму и версию приложения
	# Это надо чтобы избежать ошибки 'Old_version' при регистрации номера телефона
	# если ошибка возникла, скачать новую инсталяху
	python3 dexMD5.py WhatsApp.apk  &>/dev/null

	# сохранить данные из version.txt и md5.txt в переменные
	version=$(cat version.txt)
	md5=$(cat md5.txt)

	# записать эти переменные в файл yowsup/env/env_android.py
	sed -i "s/_MD5_CLASSES = .*/_MD5_CLASSES = '"$md5"'/" yowsup/yowsup/env/env_android.py

	sed -i "s/\<_VERSION = .*/_VERSION = '"$version"'/" yowsup/yowsup/env/env_android.py

	# снова процесс установки, не знаю зачем, так в неоф мануале было
	cd yowsup
	python3 setup.py build &>/dev/null
	python3 setup.py install &>/dev/null
    kill $timer_func_pid
    echo
    echo -e "${GREEN}Yowsup installed succesfull!${NORMAL}"
    
}



while [ -n "$1" ]
do
case "$1" in
-w) run_bot ;;
-i) install ;;
-r) register_bot ;;
*) echo "$1 is not an option" ;;
esac
shift
done

