PYTHONPATH := .:$(HOME):$(HOME)/BPRC/:$(HOME)/BPRC/bprc:$(HOME)/BPRC/tests/


init:
	pip3 install -r requirements.txt

test-coverage: init
	coverage run -m unittest -v

test: init
	python3 -m unittest -v

tests: test

quiet-test: init
	python3 -m unittest

clean:
	rm -f *.out.*
	rm -f *.log
	rm -f coverage.xml
	rm -f .coverage
	rm -f *.deb
	rm -rf build
	rm -rf dist

pypi:
	python3 setup.py register bdist upload

pypi-wheel:
	python3 setup.py register sdist bdist_wheel upload


.PHONY:	test
