## Pytest tutorial

This tutorial extends [Flask blog example](https://github.com/pallets/flask/tree/master/examples/tutorial) (`flaskr`) and adds a
few more test functions to showcase pytest features.

### Differences with `flaskr`

The blog table has an addition boolean (integer) column called `is_published`.

The `register` view can optionally use a util function that enforces strong passwords. This feature can be enabled by
setting `USE_STRONG_PASSWORD` to `True` in `instance/config.py`.