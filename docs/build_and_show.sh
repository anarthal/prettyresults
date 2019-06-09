#!/bin/bash

BUILD_DIR=/tmp/analyzer_docs
sphinx-build -b html . $BUILD_DIR
python3 -c "import webbrowser; webbrowser.open(\"file://$BUILD_DIR/reference.html\")"
