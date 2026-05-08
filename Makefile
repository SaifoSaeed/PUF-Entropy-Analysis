.PHONY: clean convert test all download

DF_DIR := datasets

all: clean download convert xors crps run plot

run:
	python src/run_test.py -p proc_datasets
	python src/run_test.py -p xor_datasets
	python src/run_test.py -p crp_datasets

plot:
	python src/plot.py -p proc_datasets
	python src/plot.py -p xor_datasets
	python src/plot.py -p crp_datasets

crps:
	python src/gen_crps.py

xors:
	python src/gen_xors.py

convert:
	python src/convert.py

download:
ifeq ("$(wildcard $(DF_DIR).zip)","")
	curl https://zenodo.org/records/14162308/files/Dataset.zip?download=1 -o $(DF_DIR).zip
else
	echo "File datasets.zip already exists"
endif
	mkdir -p $(DF_DIR)
	tar -xf $(DF_DIR).zip -C "$(DF_DIR)"
	cp  -r $(DF_DIR)\Dataset Dataset
	rm -rf $(DF_DIR)
	mv Dataset $(DF_DIR)
	
clean:
	rm -rf $(DF_DIR) proc_$(DF_DIR) $(DF_DIR).zip Dataset xor_datasets crp_datasets