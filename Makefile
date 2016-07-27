#TODO fix this.
init:
    pip3 install -r requirements.txt

test:
    python3 -m unittest -v

.PHONY init test
