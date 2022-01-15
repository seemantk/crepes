#!/usr/bin/env python3
# Copyright (c) 2020-2021 Seemant Kulleen <seemantk@gmail.com>

# TODO:
# --force to overwrite an existing dir tree (remove the old one)
# move all this into the crepes binary under an --init flag



import os, sys
import argparse
from cfn_tools import load_yaml, dump_json, dump_yaml

# Parameters
parser = argparse.ArgumentParser(description='breakdown a YAML CloudFormation template into component destination directory')
parser.add_argument('destdir', metavar='destdir', type=str, default='', help='destination directory')
parser.add_argument('--source', dest='template', type=str, help='source CloudFormation template')
args = parser.parse_args()

# Constants
SECTIONS = ['Description', 'Metadata', 'Parameters', 'Mappings','Conditions', 'Transform', 'Resources', 'Outputs']


#
# Main Function
#
def main():
    if args.template:
        # Read the introspected CloudFormer template
        with open(args.template) as f:
            current = load_yaml(f)

    # Create the section directories if they don't exist
    for i, section in enumerate(SECTIONS, start=1):
        # Create a directory for the section of the template, e.g 01_Description/
        secdir = '_'.join([str(i).zfill(2), section])

        try:
            os.makedirs(os.path.join(args.destdir, secdir), exist_ok=True)

            if(i == 1): # Write out the description file
                if args.template: # Create a description placeholder
                    process_description(secdir, current[section])
                else:
                    process_description(secdir, 'Description of the stack goes here.')

            elif(i == 7): # Process the AWS Resources
                if args.template:
                    process_resources(secdir, current[section])
            else:
                if args.template:
                    process_section(secdir, section, current[section])
        except KeyError:
            continue

# Helper Functions
def process_description(secdir, description):
    with open(os.path.join(args.destdir, secdir, 'description.txt'), 'w') as f:
        f.write(description)


def process_resources(secdir, resources):
    for resname in resources:
        # Grab the AWS resource type (e.g. AWS::EC2::LaunchInstance)
        resource = resources[resname]
        resource_type = resource['Type'].split('::')
        resource_type.reverse()
        # Discard the 'AWS' part
        resource_type.pop()
        resource_type.reverse()
        dirname = os.sep.join([args.destdir, secdir, os.sep.join(resource_type)])
        filename = '.'.join([resname, 'yml'])

        # put each resource into a directory nmed for its type
        try:
            os.makedirs(dirname)
        except FileExistsError:
            pass

        # Write out the object into its own file
        with open(os.path.join(dirname, filename), 'w') as f:
            f.write(dump_yaml({'%s' % resname: resource}))



def process_section(secdir, section, content):
    print("processing %s" % secdir)
    with open(os.path.join(args.destdir, secdir, '%s.yml' % section.lower()), 'w') as f:
        f.write(dump_yaml({'%s' % content}))


if __name__ == "__main__":
    main()
