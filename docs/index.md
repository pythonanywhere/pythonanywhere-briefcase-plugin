# PythonAnywhere

A [Briefcase](https://briefcase.readthedocs.io/) publication channel plugin that deploys static web apps to [PythonAnywhere](https://www.pythonanywhere.com/).

!!! warning

    This package depends on the publication channels feature in Briefcase, which has not been included in a release yet. Until it is released, install Briefcase from main:

    ```
    pip install git+https://github.com/beeware/briefcase@main
    ```

## Prerequisites

* A PythonAnywhere account
* An API token (from your [Account page](https://www.pythonanywhere.com/account/#api_token) on PythonAnywhere)

## Installation

Install the plugin into your Briefcase project's virtual environment:

```console
(venv) $ pip install briefcase-pythonanywhere
```

## Quick start

First, build and package your web app:

```console
(venv) $ briefcase create web static
(venv) $ briefcase build web static
(venv) $ briefcase package web static
```

Set your PythonAnywhere API token:

```console
(venv) $ export API_TOKEN=your-api-token-here
```

Then publish:

```console
(venv) $ briefcase publish web static
```

If `briefcase-pythonanywhere` is the only publication channel installed, it will be selected automatically. If you have multiple channels installed, specify the channel explicitly:

```console
(venv) $ briefcase publish web static --channel pythonanywhere
```

Your app will be deployed to `https://<username>.pythonanywhere.com/`.

## Configuration

Configuration options can be added to the `tool.briefcase.app.<appname>.pythonanywhere` section of your `pyproject.toml` file.

### `username`

Your PythonAnywhere username. If not specified, the plugin will check the `PYTHONANYWHERE_USERNAME` environment variable, then fall back to the system username.

```toml
[tool.briefcase.app.myapp.pythonanywhere]
username = "mypauser"
```

### `domain`

The domain name for your PythonAnywhere webapp. If not specified, defaults to `<username>.pythonanywhere.com`.

```toml
[tool.briefcase.app.myapp.pythonanywhere]
domain = "www.mycustomdomain.com"
```

## Environment variables

The following environment variables are used by the plugin:

### `API_TOKEN`

**Required.** Your PythonAnywhere API token. Obtain this from the [API Token tab](https://www.pythonanywhere.com/account/#api_token) on your PythonAnywhere Account page.

### `PYTHONANYWHERE_USERNAME`

Your PythonAnywhere username. Used as a fallback if `username` is not set in `pyproject.toml`.

### `PYTHONANYWHERE_DOMAIN`

The PythonAnywhere domain suffix. Defaults to `pythonanywhere.com`. This is useful if you are using a regional PythonAnywhere instance (e.g., `eu.pythonanywhere.com`).

## Contributing

Development requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

Clone the repository and install the development dependencies:

```console
$ git clone https://github.com/pythonanywhere/briefcase-pythonanywhere.git
$ cd briefcase-pythonanywhere
$ uv sync
```

Set up pre-commit hooks:

```console
$ uvx pre-commit install
```

This will run linting (ruff), formatting, type checking (ty), and other checks automatically on every commit.

To run the test suite:

```console
$ uv run pytest
```

To run pre-commit checks manually against all files:

```console
$ uvx pre-commit run --all-files
```

## How it works

When you run `briefcase publish web static`, the plugin:

1. Reads the packaged `.zip` distribution artifact produced by `briefcase package web static`.
2. Extracts the archive and uploads its contents to `/home/<username>/<app_name>/` on PythonAnywhere.
3. Creates a new webapp (or updates the existing one) with a static file mapping from `/` to the uploaded directory.
4. Reloads the webapp so the changes take effect.
