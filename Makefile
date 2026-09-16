.PHONY: api webapp start

api:
	.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

webapp:
	npm --prefix webapp run dev

start:
	$(MAKE) -j2 api webapp
