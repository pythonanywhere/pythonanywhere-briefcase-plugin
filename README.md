# briefcase-pythonanywhere

A [Briefcase](https://briefcase.readthedocs.io/) publication channel plugin for deploying static web apps to [PythonAnywhere](https://www.pythonanywhere.com/).

## Prerequisites

* A PythonAnywhere account
* An API token (from your [Account page](https://www.pythonanywhere.com/account/#api_token))

## Installation

```console
$ pip install briefcase-pythonanywhere
```

## Quick start

Build and package your web app:

```console
$ briefcase create web static
$ briefcase build web static
$ briefcase package web static
```

Set your PythonAnywhere API token:

```console
$ export API_TOKEN=your-api-token-here
```

Publish:

```console
$ briefcase publish web static
```

Your app will be deployed to `https://<username>.pythonanywhere.com/`.

## Documentation

Full documentation is available at [https://briefcase.pythonanywhere.com/](https://briefcase.pythonanywhere.com/).

## Contributing

Development requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```console
$ git clone https://github.com/pythonanywhere/briefcase-pythonanywhere.git
$ cd briefcase-pythonanywhere
$ uv sync
$ uvx pre-commit install
$ uv run pytest
```

## License

MIT license.
