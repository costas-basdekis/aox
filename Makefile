setup:
	pip install -r test_requirements.txt
	pip install -r requirements.txt
.PHONY: setup

test:
	pytest $(ARGS)
.PHONY: test

commit_and_tag: commit tag
.PHONY: commit_and_tag

commit:
	git add aox/version
	git commit -C "Bump version to v$(python3 aox/version.py)"
.PHONY: commit

tag:
	git tag -a "v$(python3 aox/version.py)" -m "Release v$(python3 aox/version.py)" -e
.PHONY: tag

build_and_publish: build publish
.PHONY: build_and_publish

build:
	rm -rf build/ dist/
	python3 -m build
.PHONY: build

publish:
	twine upload dist/*
.PHONY: publish
