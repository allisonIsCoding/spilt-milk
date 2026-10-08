.PHONY: run test publish skill

run:
	PYTHONPATH=src python3 -m milk_carton --config config/default.json --png --sweep --out outputs

test:
	PYTHONPATH=src python3 -m pytest -q

publish:
	scripts/publish.sh

skill:
	python3 scripts/build_skill.py
