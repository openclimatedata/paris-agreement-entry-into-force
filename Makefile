all: data/paris-agreement-entry-into-force.csv

emissions-table:
	wget -O archive/table.pdf "http://unfccc.int/files/paris_agreement/application/pdf/10e.pdf"
	@echo tabula-table.csv needs to be extracted manually using Tabula ...
	@echo See http://tabula.technology/

treaty-collection:
	wget -O archive/treaty-collection.html 'https://treaties.un.org/pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&lang=en'

data/paris-agreement-entry-into-force.csv: treaty-collection
	python scripts/process.py

clean:
	rm data/*.csv archive/table.pdf archive/treaty-collection.html

.PHONY: clean emissions-table treaty-collection emissions-table
