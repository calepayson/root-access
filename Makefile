.PHONY: app model

venv:
	python -m venv venv

setup: venv
	source venv/bin/activate && pip install -r requirements.txt

app:
	cd app && ../venv/bin/python app.py

data:
	./venv/bin/python data_pipeline/get_data.py
	./venv/bin/python data_pipeline/sif_preprocess.py
	./venv/bin/python data_pipeline/moisture_preprocess.py
	./venv/bin/python data_pipeline/merge_data.py

model:
	./venv/bin/python model/model.py
	mv sif_moisture_predicted.parquet app/data/sif_moisture/sif_moisture_predicted.parquet


