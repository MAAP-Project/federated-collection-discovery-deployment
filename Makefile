.PHONY: install
install:
	npm install
	npm install -g yarn
	poetry install
	pre-commit install

.PHONY: deploy
deploy:
	poetry run npx cdk deploy --all --require-approval never --outputs-file cdk-output.json


.PHONY: destroy
destroy:
	poetry run npx cdk destroy --all 
