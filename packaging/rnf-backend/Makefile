all:
	python3 -m venv venv
	. venv/bin/activate
	python3 -m pip install -r ../../requirements.txt
	pyinstaller --onefile ../../main.py -n api

clean:
	rm -rf api.spec build dist