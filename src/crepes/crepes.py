#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

import os, boto3
import argparse
from cfn_tools import load_yaml, dump_yaml, dump_json
from jinja2 import Template
import importify


#
# Helper functions
#
# Read raw YAML file and process as a Jinja template
def process_jinja_template(filename, kwargs):
    with open(filename) as f:
        contents = f.read()

    template = Template(contents)

    return load_yaml(template.render(**kwargs))

# Assemble all the components of a stack into a single cloudformation::stack object
def assemble(stack, kwargs, imports={}):
    # Create a dictionary to hold all the information
    cfn_stack = { 'AWSTemplateFormatVersion': '2010-09-09' }

    # Section names start with '0'
    sections = [l for l in os.listdir(stack) if l.startswith('0')]
    sections.sort()

    for section in sections:
        sec = section.split('_')[1]

        # Create an empty dictionary key for this section for all the files to add their data
        cfn_stack[sec] = {}

        # Traverse the directory hierarchy, parsing all files along the way
        for dirpath, dirs, files in os.walk(os.path.join(stack, section)):
            for f in files:
                # Process each file as a Jinja template first
                contents = process_jinja_template(os.path.join(dirpath, f), kwargs)
                filename = f.lower()

                if filename.endswith('.yml') or filename.endswith('yaml'):
                    # Process YAML files (most everything)
                    print("Flipping %s" % os.path.relpath(os.path.join(dirpath, f), '.'))

                    # if this is an import template (rare)
                    if sec == 'Resources' and imports:
                        # Only import keys specified in the file in arg.imports
                        keys = [key for key in contents.keys() if key in imports.keys()]
                    else:
                        keys = contents.keys()

                    for key in keys:
                        # Append each YAML object to the cfn_stack
                        if contents[key]:
                            cfn_stack[sec][key] = contents[key]
                elif filename.endswith('.txt') or filename.endswith('text'):
                    # Process the description text file
                    cfn_stack[sec] = contents
                else:
                    # Bypass files with other content
                    continue

    return {k: v for k, v in cfn_stack.items() if v} # discard null/empty keys


def parse_command_line_arguments():
    # Helper to parse keyword arguments for Jinja variables
    class ParseKwargs(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split('=')
                getattr(namespace, self.dest)[key] = value


    # Available command line arguments and their defaults
    parser = argparse.ArgumentParser(description='process jinja YAML files and assemble into a CloudFormation template')
    parser.add_argument('directory', metavar='dir', type=str, help='source directory')
    parser.add_argument('--region', dest='region', type=str, help='AWS Region')
    parser.add_argument('--output', dest='outfile', type=str, default='CloudFormation.yml', help='output CloudFormation YAML file')
    parser.add_argument('--import', dest='imports', type=str, help='name of file to output the resources list')
    parser.add_argument('--kwargs', dest='kwargs', nargs='*', action=ParseKwargs, help="list of KEY=value pairs")

    # return the parsed command line arguments
    return parser.parse_args()


def get_aws_metadata(region, kwargs={}):
    # Retrieve info about the specified AWS region
    ec2   = boto3.setup_default_session(region_name=region)
    ec2   = boto3.client('ec2')
    zones = ec2.describe_availability_zones()['AvailabilityZones']

    kwargs['REGION']  = region
    kwargs['AZs']     = [z['ZoneName'] for z in zones]
    kwargs['AZcodes'] = [z.split('-')[2] for z in kwargs['AZs']]

    return kwargs


#
# Main loop
#
def main():
    args = parse_command_line_arguments()

    # Create the destination dir, if it doesn't exist
    outdir = os.path.dirname(os.path.abspath(args.outfile))
    os.makedirs(outdir, exist_ok=True)

    kwargs = get_aws_metadata(args.region, kwargs=args.kwargs or {})

    # If importing the imports template is processed through Jinja, otherwise we get an empty dict
    imports_template = process_jinja_template('ImportedResources.yml', kwargs) if args.imports else {}

    # Assemble the stack into a dict and convert that to YAML 
    # The imports_template variable is {} if not importing
    stack = assemble(args.directory, kwargs, imports=imports_template)

    if args.imports:
        # Import template is not allowed to have an Outputs section
        stack.pop('Outputs', None)

        # Create artifacts for importing resources
        importify.importfiy(stack, args.imports)

    formation = dump_yaml(stack)

    with open(args.outfile, 'w') as f: f.write(formation)

# Execute if run as a script
if __name__ == "__main__":
    main()
