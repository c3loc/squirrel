# squirrel

squirrel is the tooling the CCCV Einkauf uses to organize orders.

We believe strongly in the credo that **all creatures are welcome**. However, as sometimes people are not tolerant towards each other, this project has a [Code of Conduct](CODE_OF_CONDUCT.md) and will enforce it.

## Usage

For usage, see the [docs directory](docs).

## Setup

You need to install all requirements from requirements.txt and have a config file that specifies a secret key. 

### Setup the venv

```sh
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# For development only
pip install -r requirements-dev.txt
```

### Configure squirrel

For squirrel to run, you need to configure it. The supplied [`settings.example.ini`](src/settings.example.ini) lists
all possible settings.

Put your configuration file at `src/settings.ini`.

You need to set at least a `SECRET_KEY` or squirrel will not start.

### Configure the web server

Your web server must encrypt connections. squirrel will not work properly without HTTPS in production mode.

Your web server must serve requests for `/public` from the directory `squirrel`.

If squirrel is installed in `/var/www/squirrel`, the requests must be served from `/var/www/squirrel/squirrel/public`.

Example for nginx:

```
location /public {
    root /var/www/squirrel/src;
}
```

### Initialize and update squirrel 

When you first install squirrel and when you update it, you have to perform some extra steps. In the `src` directory, run:

``` 
# Migrate the database
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic

# Create a superuser with all rights
# You only have to do this when installing. Updating preserves all data.
python3 manage.py createsuperuser
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
* `flake8` for syntax checking

If any of those fail, you need to fix all problems before you can commit
your change. If you need help with any of it, please open an issue.

### Tests

When you push to the repository on github or update your Pull Request,
all django tests run automatically. Please try to add tests for everything
you’re changing/adding.

If you need help with that, you can always open an issue and ask for help.

## Acknowledgements

* The squirrel icon used as favicon was designed by [Max Gaines](https://thenounproject.com/icon/27067/)