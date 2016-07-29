PYTHONPATH := .:$(HOME):$(HOME)/BPRC/:$(HOME)/BPRC/bprc:$(HOME)/BPRC/tests/"


init:
	pip3 install -r requirements.txt

test:
	python3 -m unittest -v

.PHONY:	test
