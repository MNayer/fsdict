.PHONY: format lint testpush push clean

all: format lint build

clean:
	rm -rf dist

format:
	black src/

lint:
	pylint --errors-only src/

build:
	python -m build

testpush:
	twine upload -r testpypi dist/*

push:
	twine upload dist/*
