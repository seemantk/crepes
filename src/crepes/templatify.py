#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

from cfn_tools import load_yaml
from jinja2 import Template

# Read raw YAML file and process as a Jinja template
def process_jinja(filename, kwargs):
    with open(filename) as f:
        contents = f.read()

    # initialize jinja with the contents of the YAML file
    template = Template(contents)

    # Render the JINJA template, convert it to a YAML document, and return that to the caller
    return load_yaml(template.render(**kwargs))
