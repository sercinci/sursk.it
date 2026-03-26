.PHONY: backend frontend test build-data

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	pytest

build-data:
	python3 scripts/build_data.py
