.PHONY: run test publish skill

run:
	PYTHONPATH=src python3 -m milk_carton --config config/default.json --png --out outputs
	PYTHONPATH=src python3 -m milk_carton --config config/tipped.json --png --sweep --out outputs/tipped

test:
	PYTHONPATH=src python3 -m pytest -q

publish:
	scripts/publish.sh

skill:
	python3 scripts/build_skill.py
