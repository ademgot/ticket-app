.PHONY: api webapp start seed

api:
	.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

webapp:
	npm --prefix webapp run dev

start:
	$(MAKE) -j2 api webapp

seed:
	PYTHONPATH=. .venv/bin/python scripts/seed_venues_events.py
