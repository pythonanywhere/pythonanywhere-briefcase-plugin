# Tutorial - Deploy to PythonAnywhere

This tutorial picks up where [Tutorial 6 - Put it on the web!](https://tutorial.beeware.org/en/latest/tutorial/tutorial-6/) of the BeeWare Tutorial leaves off. In that tutorial, you built a static web app and ran it locally with `briefcase run web`. Now we'll publish it to PythonAnywhere so it's accessible on the internet.

/// admonition | Prerequisites
    type: info

Before starting, make sure you have:

* Completed the BeeWare tutorial through [Tutorial 6](https://tutorial.beeware.org/en/latest/tutorial/tutorial-6/) (or at least run `briefcase create web static` and `briefcase build web static`)
* A [PythonAnywhere](https://www.pythonanywhere.com/) account
* An API token from your [Account page](https://www.pythonanywhere.com/account/#api_token)

///

## Install the plugin

With your BeeWare tutorial virtual environment active, install the plugin:

/// tab | macOS

```console
(beeware-venv) $ pip install pythonanywhere-briefcase-plugin
```

///

/// tab | Linux

```console
(beeware-venv) $ pip install pythonanywhere-briefcase-plugin
```

///

/// tab | Windows

```doscon
(beeware-venv) C:\...>pip install pythonanywhere-briefcase-plugin
```

///

## Package the app

In Tutorial 6, you ran the app locally with `briefcase run web`. To publish it, we first need to package the app into a distributable artifact:

/// tab | macOS

```console
(beeware-venv) $ briefcase package web static

[helloworld] Packaging Hello World...
...

[helloworld] Packaged dist/Hello World-0.0.1.web.zip
```

///

/// tab | Linux

```console
(beeware-venv) $ briefcase package web static

[helloworld] Packaging Hello World...
...

[helloworld] Packaged dist/Hello World-0.0.1.web.zip
```

///

/// tab | Windows

```doscon
(beeware-venv) C:\...>briefcase package web static

[helloworld] Packaging Hello World...
...

[helloworld] Packaged dist\Hello World-0.0.1.web.zip
```

///

This creates a ZIP file containing all the static files needed to serve your app.

## Set your API token

The plugin needs your PythonAnywhere API token to upload files and configure the webapp. Set it as an environment variable:

/// tab | macOS

```console
(beeware-venv) $ export API_TOKEN=your-api-token-here
```

///

/// tab | Linux

```console
(beeware-venv) $ export API_TOKEN=your-api-token-here
```

///

/// tab | Windows

```doscon
(beeware-venv) C:\...>set API_TOKEN=your-api-token-here
```

///

Replace `your-api-token-here` with the token from your [Account page](https://www.pythonanywhere.com/account/#api_token).

//// admonition | Username
    type: note

The plugin needs to know your PythonAnywhere username to upload files to the right place. By default, it uses the `PYTHONANYWHERE_USERNAME` environment variable, falling back to your local system username.

If you're running this from a PythonAnywhere console, the username is detected automatically -- no extra configuration needed.

If you're running locally and your PythonAnywhere username is different from your local system username, either set the environment variable:

/// tab | macOS

```console
(beeware-venv) $ export PYTHONANYWHERE_USERNAME=your-pa-username
```

///

/// tab | Linux

```console
(beeware-venv) $ export PYTHONANYWHERE_USERNAME=your-pa-username
```

///

/// tab | Windows

```doscon
(beeware-venv) C:\...>set PYTHONANYWHERE_USERNAME=your-pa-username
```

///

or add it to the `pyproject.toml` of your app:

```toml
[tool.briefcase.app.helloworld.pythonanywhere]
username = "your-pa-username"
```

////

## Publish

Now, publish the app to PythonAnywhere:

/// tab | macOS

```console
(beeware-venv) $ briefcase publish web static
```

///

/// tab | Linux

```console
(beeware-venv) $ briefcase publish web static
```

///

/// tab | Windows

```doscon
(beeware-venv) C:\...>briefcase publish web static
```

///

The plugin will:

1. Extract the packaged ZIP file.
2. Upload the contents to `/home/<your-username>/helloworld/` on PythonAnywhere.
3. Create a webapp (or update the existing one) with a static file mapping pointing `/` to that directory.
4. Reload the webapp.

Once it's done, your app is live at `https://<your-username>.pythonanywhere.com/`!

## How does this work?

In Tutorial 6, Briefcase started a local web server to serve your static web app. The `publish` command takes the same static files and deploys them to PythonAnywhere's infrastructure instead.

PythonAnywhere serves the files as a static website -- no Python process runs on the server. The Python code in your app runs in the *browser*, using [PyScript](https://pyscript.net), just as it did when you ran it locally.

The plugin uses the [PythonAnywhere API](https://help.pythonanywhere.com/pages/API/) to upload files and configure the webapp, which is why the API token is required.

## Next steps

Your app is now live on the internet. From here you might want to:

* **Use a custom domain** -- configure a `domain` in your `pyproject.toml` to serve the app from your own domain name. See the [Configuration](index.md#configuration) section.
* **Continue the BeeWare tutorial** -- [Tutorial 7](https://tutorial.beeware.org/en/latest/tutorial/tutorial-7/) covers adding third-party libraries to your app.
