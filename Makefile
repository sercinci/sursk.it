.PHONY: backend frontend test build-data install

VENV := .venv
PY   := $(VENV)/bin/python

$(VENV):
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip

install: $(VENV)
	$(PY) -m pip install -r backend/requirements.txt

backend: install
	cd backend && ../$(PY) -m uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	pytest

build-data:
	python3 scripts/build_data.py
