PYTHONPATH := .:$(HOME):$(HOME)/BPRC/:$(HOME)/BPRC/bprc:$(HOME)/BPRC/tests/


init:
	pip3 install -r requirements.txt

test-coverage: init
	coverage run -m unittest -v

test: init
	python3 -m unittest -v

clean:
	rm -f *.out.*
	rm -f *.log
	rm -f coverage.xml
	rm -f .coverage
	rm -f *.deb
	rm -rf build
	rm -rf dist


.PHONY:	test
