# Federated Collection Discovery Deployment

## About

This is a deployment repo for MAAP's instance of the
[Federated Collection Discovery application](https://github.com/developmentseed/federated-collection-discovery).

The resources get deployed to the SMCE-MAAP AWS account by the
[`deploy`](./.github/workflows/deploy.yaml) Github Actions workflow where
you must specify the deployment environment (`dev` or `test`) and the
API version to use.

The Github Action workflow will deploy:

- the Federated Collection Search API
  - Lambda function with an API gateway endpoint
  - alias for a url at maap-project.org
- the Federated Collection Search client application
  - React app built by yarn and uploaded to S3, served by CloudFront
  - alias for a url at maap-project.org

### Gotchas

- The corresponding alias records for maap-project.org are managed in the UAH-MAAP
AWS account and must be manually entered/updated to redirect requests to the
resources in this stack.

- We have to checkout the client app repo and build the React app then upload the
contents to the S3 bucket after it is deployed. Maybe there is a better way to do
this!

## Deployment environments

Each deployment requires several attributes to be specified, these are handled
in the
[Github Environments](https://github.com/MAAP-Project/federated-collection-discovery-deployment/settings/environments)
and are passed as environment variables in the `deploy` step of the workflow.

The `dev` and `test` environments share some of these in common but the custom
domain names differ between the two environments:

- `*.dit.maap-project.org` for the `test` environment
- `*.maap-project.org` for the `dev` environment

## Local development

The AWS infrastructure is defined in a Python CDK application.
You can install the Python dependencies for the project with
this command from the [`Makefile`](./Makefile)
(requires [Node](https://nodejs.org/en/download/package-manager/current)
and [uv](https://docs.astral.sh/uv/getting-started/installation/)):

```shell
make install
```

This will create a virtual environment if you don't already have one, will
use an existing one if it is activated.

## Non-Github Actions deployments

To deploy the resources to an AWS account from your local environment,
you will need to define some variables in your environment (or in a `.env-cdk` file).
Reference [`config.py`](./infrastructure/config.py) for all of the possible options.

At a minimum you will want to define `STAC_API_URLS` which will define the list of
STAC APIs that the Federated Collection Discovery API will search.

You can put this in `.env-cdk` which will get automatically used by the CDK app:

```shell
# comma separated list of STAC API urls:
STAC_API_URLS=https://stac.maap-project.org/,https://openveda.cloud/api/stac/,https://catalogue.dataspace.copernicus.eu/stac
```

To deploy the AWS resources:

```shell
make deploy
```

This will deploy the API and create the infrastructure for the client application,
but you will still need to build the client application and upload it to the S3
bucket to complete the deployment!
Check out the [`deploy workflow`](./.github/workflows/deploy.yaml) for inspiration
if you want to do this locally.

**TODO**: Add docker-based client app build process

To destroy the stack:

```shell
make destroy
```
