python ?= python3.4

all: git_devbliss.egg_info/

git_devbliss.egg_info/: bin/pip
	bin/pip install --editable .

test: flake8 coverage all

flake8: bin/flake8 all
	bin/flake8 setup.py git_devbliss

coverage: bin/coverage all
	bin/coverage run --source=git_devbliss,setup.py -m unittest discover -vfb
	bin/coverage html
	bin/coverage report --fail-under=100 && bin/coverage html

bin/coverage: bin/pip
	bin/pip install coverage
bin/flake8: bin/pip
	bin/pip install flake8
bin/pip: bin/python
	bin/python -m ensurepip --upgrade
bin/python:
	$(python) -m venv --without-pip .

clean-dist:
	rm -rf htmlcov/ .coverage
	rm -rf *.egg-info/ *.egg build/ dist/
	find . -name __pycache__ -type d | xargs rm -rf
clean: clean-dist
	rm -rf bin/ lib/ include/ pyvenv.cfg
