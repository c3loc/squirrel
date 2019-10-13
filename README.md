# squirrel

squirrel is the tooling the CCCV Einkauf uses to organize orders.

We believe strongly in the credo that **all creatures are welcome**. However, as sometimes people are not tolerant towards each other, this project has a [Code of Conduct](CODE_OF_CONDUCT.md) and will enforce it.

## Usage

For usage, see the [docs directory](docs):

## Setup

### Setup the venv

```sh
virtualenv -p python3.6 venv
source venv/bin/activate

pip install -r requirements.txt

# For development only
pip install -r requirements-dev.txt
```

## Contributions

To contribute, please read through this section before submitting a PR.
Everything described below is automatically tested in with Github Actions.

The included pre-commit hook performs all checks detailed below. Please set it up
with 

```shell script
ln -s $PWD/pre-commit.sh .git/hooks/pre-commit
``` 
 
### Commit message style

Your commit message adheres to the [conventional commit standard](https://www.conventionalcommits.org/en/v1.0.0/), version 1.0.0.

TL;DR: Your commit must start with a type which has to be one of:

* `fix:` for bug fixes (patch version increment)
* `feat:` for new features (minor version increment)
* `docs:` for documentation changes
* `test:` for changes to tests only

If you introduce a breaking change, add a `!` after the type. This also requires a major version update.

### Linting

The code has to pass a flake8 test with the [.flake8](.flake8) config for this repository.

You can install and run it manually with

```
pip install flake8
flake8 squirrel/
```

### Tests

The code has to pass all defined tests. If you add new functionality, you should add tests for it.

You can manually run tests with

```
cd squirrel
python manage.py test
```
