.PHONY: install
install:
	npm install
	npm install -g yarn
	uv sync --group dev
	pre-commit install

.PHONY: deploy
deploy:
	uv run npx cdk deploy --all --require-approval never --outputs-file cdk-output.json


.PHONY: destroy
destroy:
	uv run npx cdk destroy --all 
