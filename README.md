## Pytest tutorial

This tutorial extends [Flask blog example](https://github.com/pallets/flask/tree/master/examples/tutorial) (`flaskr`) and adds a
few more test functions to showcase pytest features.

### Differences with `flaskr`

The blog table has an addition boolean (integer) column called `is_published`.

The `register` view can optionally use a util function that enforces strong passwords. This feature can be enabled by
setting `USE_STRONG_PASSWORD` to `True` in `instance/config.py`.

The index view fetches a quote from a remote service and shows it at the bottom of the page.

### How to test

Run `pip install -e .[dev]` in your virtual environment.

Before running the server, you need to initialize the database by running `./run.sh init-db`.
Then you can start the server by calling `./run.sh`. You can also call this script with all the flags that Flask CLI accepts.
The server should start on port 5000.

To test the code, run `pytest`.
To generate `coverage` report, run `coverage run -m pytest`.
To see the generated report, run `coverage report`.
