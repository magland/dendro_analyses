#!/bin/bash

set -ex

dendro make-app-spec-file --app-dir dendro1 --spec-output-file dendro1/spec.json

dendro make-app-spec-file --app-dir cebra1 --spec-output-file cebra1/spec.json
