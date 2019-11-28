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
Everything described below is automatically tested in with Github Actions and with
the supplied pre-commit configuration.

### Setup

Activate the venv and setup pre-commit

```
# Activate the venv
source venv/bin/activate

# Set up pre-commit
pre-commit install --hook-type commit-msg --hook-type pre-commit
```

That’s it. Now, every time before a commit is created, the defined checks
will run.

### Formatting and Linting

`pre-commit` runs:

* `isort` for include sorting
* `black` for code formatting
* `flak8` for syntax checking

If any of those fail, you need to fix all problems before you can commit
your change. If you need help with any of it, please open an issue.

### Tests

When you push to the repository on github or update your Pull Request,
all django tests run automatically. Please try to add tests for everything
you’re changing/adding.

If you need help with that, you can always open an issue and ask for help.
