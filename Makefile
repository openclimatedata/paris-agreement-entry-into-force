all: venv
	git pull
	./venv/bin/python scripts/process.py
	@git diff data

emissions-table:
	wget -O archive/table.pdf "http://unfccc.int/files/paris_agreement/application/pdf/10e.pdf"
	@echo tabula-table.csv needs to be extracted manually using Tabula ...
	@echo See http://tabula.technology/

venv: scripts/requirements.txt
	[ -d ./venv ] || python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -Ur scripts/requirements.txt
	touch venv

clean:
	rm -rf data/*.csv venv

.PHONY: clean emissions-table treaty-collection emissions-table
