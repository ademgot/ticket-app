.PHONY: api webapp seed new-migration migrate

# DB
new-migration:
	@test -n "$(m)" || (echo 'usage: make new-migration m="description"' >&2; exit 1)
	@next=$$(find api/alembic/versions -maxdepth 1 -name '*.py' -exec basename {} \; \
		| cut -d_ -f1 | grep -E '^[0-9]+$$' | sort -n | tail -1); \
	next=$$(printf '%05d' $$(( $${next:-0} + 1 ))); \
	cd api && ../.venv/bin/alembic revision -m "$(m)" --rev-id $$next

migrate:
	cd api && ../.venv/bin/alembic upgrade head

seed:
	PYTHONPATH=. .venv/bin/python scripts/seed_venues_events.py


# API
api:
	.venv/bin/uvicorn api.main:app --reload --host 127.0.0.1 --port 8000


# Webapp
webapp:
	npm --prefix webapp run dev