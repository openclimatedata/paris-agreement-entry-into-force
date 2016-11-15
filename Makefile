all:
	python scripts/process.py
	@git diff data

emissions-table:
	wget -O archive/table.pdf "http://unfccc.int/files/paris_agreement/application/pdf/10e.pdf"
	@echo tabula-table.csv needs to be extracted manually using Tabula ...
	@echo See http://tabula.technology/

clean:
	rm data/*.csv archive/table.pdf cache/*

.PHONY: clean emissions-table treaty-collection emissions-table
