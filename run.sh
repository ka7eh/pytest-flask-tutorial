#!/bin/sh

export FLASK_APP=flaskr
export FLASK_ENV=development

flask "${1:-run}"
