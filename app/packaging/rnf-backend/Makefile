all:
	python3 -m venv venv
	venv/bin/python3 -m pip install -r ../../requirements.txt
	venv/bin/pyi-makespec --onefile -p ../../../app ../../main.py -n api
	venv/bin/pyinstaller api.spec

clean:
	rm -rf api.spec build dist