init:
	pip install virtualenv==20.0.35 -i https://mirrors.aliyun.com/pypi/simple/
	virtualenv venv
#	.\venv\Scripts\activate
	.\venv\Scripts\pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

install:
	.\venv\Scripts\pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/