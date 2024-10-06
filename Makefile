.PHONY: app

venv:
	python -m venv venv

setup: venv
	source venv/bin/activate && pip install -r requirements.txt

app:
	cd app && ../venv/bin/python app.py
