SOURCE_GLOB=$(wildcard bin/*.py src/**/*.py tests/**/*.py examples/*.py)

IGNORE_PEP=E203,E221,E241,E272,E501,F811

export PYTHONPATH=./

.PHONY: all
all : clean lint

.PHONY: clean
clean:
	rm -fr dist/* .pytype

.PHONY: lint
lint: pylint pycodestyle flake8


.PHONY: pylint
pylint:
	pylint \
		--load-plugins pylint_quotes \
		--disable=W0511,R0801,cyclic-import \
		$(SOURCE_GLOB)

.PHONY: pycodestyle
pycodestyle:
	pycodestyle \
		--statistics \
		--count \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: flake8
flake8:
	flake8 \
		--ignore="${IGNORE_PEP}" \
		$(SOURCE_GLOB)

.PHONY: pytype
pytype:
	pytype \
		-V 3.8 \
		--disable=import-error,pyi-error \
		src/
	pytype \
		-V 3.8 \
		--disable=import-error \
		examples/

.PHONY: uninstall-git-hook
uninstall-git-hook:
	pre-commit clean
	pre-commit gc
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push

.PHONY: install-git-hook
install-git-hook:
	# cleanup existing pre-commit configuration (if any)
	pre-commit clean
	pre-commit gc
	# setup pre-commit
	# Ensures pre-commit hooks point to latest versions
	pre-commit autoupdate
	pre-commit install
	pre-commit install --hook-type pre-push


.PHONY: install
install:
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt

.PHONY: pytest
pytest:
	pytest src/ tests/

.PHONY: test-unit
test-unit: pytest

.PHONY: test
test: lint pytest


code:
	code .

.PHONY: docker
docker:
	#version="$(cat VERSION)" && docker build -t "rasa-bot:$(echo $version)" .&& docker build -t "rasa-bot:latest" .
	docker build -t "rasa-bot:latest" .
	docker run -p 5013:5013 -d --name rasa-bot rasa-bot:latest

.PHONY: dockerrun
dockerrun:
	make merge
	make train
	make run


.PHONY: version
version:
	@newVersion=$$(awk -F. '{print $$1"."$$2"."$$3+1}' < VERSION) \
		&& echo $${newVersion} > VERSION \
		&& git add VERSION \
		&& git commit -m "🔥 update version to $${newVersion}" > /dev/null \
		&& git tag "v$${newVersion}" \
		&& echo "Bumped version to $${newVersion}"

.PHONY: train-nlu
train-nlu:
	rasa train nlu

.PHONY: train
train:
	rasa train -d ./data/domain --data ./data/nlu ./data/stories --force

.PHONY: validate
validate:
	rasa data validate -d ./data/domain --data ./data/nlu ./data/stories

.PHONY: shell
shell:
	rasa shell

.PHONY: actions
actions:
	make merge
	rasa run actions

.PHONY: run
run:
	rasa run --credentials credentials.yml \
       --cors "*" --debug --endpoints endpoints.yml --enable-api

.PHONY: compress
compress:
	cd .. && zip -r ./rasa-bot.zip ./rasa-bot

.PHONY: merge
merge:
	python -m scripts.merger
