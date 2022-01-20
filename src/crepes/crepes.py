#!/usr/bin/env python3templatify.

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

import os, boto3
import argparse
from cfn_tools import load_yaml, dump_yaml, dump_json
import importify, jinjify, stackify


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
    imports_template = jinjify.process_template('ImportedResources.yml', kwargs) if args.imports else {}

    # Assemble the stack into a dict and convert that to YAML 
    # The imports_template variable is {} if not importing
    stack = stackify.assemble(args.directory, kwargs, imports=imports_template)

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
