python ?= python3.4

.PHONY: all
all: git_devbliss.egg_info/

git_devbliss.egg_info/: bin/pip
	bin/pip install --editable .

.PHONY: test
test: flake8 coverage all

.PHONY: flake8
flake8: bin/flake8 all
	bin/flake8 setup.py git_devbliss

.PHONY: coverage
coverage: bin/coverage all
	bin/coverage run --source=git_devbliss,setup.py -m unittest discover -vfb
	bin/coverage html
	bin/coverage report --fail-under=100 && bin/coverage html

bin/coverage: bin/pip
	bin/pip install coverage
bin/flake8: bin/pip
	bin/pip install flake8
bin/pip: bin/python
	#bin/python -m ensurepip --upgrade
	wget --no-check-certificate -O - https://bootstrap.pypa.io/get-pip.py | bin/python
bin/python:
	$(python) -m venv --without-pip .

.PHONY: clean-dist
clean-dist:
	rm -rf htmlcov/ .coverage
	rm -rf *.egg-info/ *.egg build/ dist/
	find . -name __pycache__ -type d | xargs rm -rf

.PHONY: clean
clean: clean-dist
	rm -rf bin/ lib/ include/ pyvenv.cfg

.PHONY: changelog
changelog:
	@$${EDITOR:-"vi"} CHANGES.md

.PHONY: version
version:
	@changelog_version=`sed -n 's/## \(.*\)/\1/p' CHANGES.md | head -n 1`; \
	echo "setting setup.py version to $$changelog_version" found in CHANGES.md; \
	sed -i '' "/git_devbliss/,/install_requires/s/version.*/version=\"$$changelog_version\",/" setup.py

.PHONY: release
release:
	@if [ -z $$DEVBLISS_VERSION ] ; then read -p 'DEVBLISS_VERSION not found. Please specify the release version: ' DEVBLISS_VERSION; fi; \
	echo "setting setup.py version to DEVBLISS_VERSION ($$DEVBLISS_VERSION)"; \
	sed -i '' "/git_devbliss/,/install_requires/s/version.*/version=\"$$DEVBLISS_VERSION\",/" setup.py

.PHONY: finish
finish:
	make test

.PHONY: upload
upload:
    bin/python setup.py register sdist upload
