#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

import os
from cfn_tools import load_yaml, dump_yaml, dump_json
import importify, jinjify

def get_aws_metadata(region, kwargs={}):
    # Retrieve info about the specified AWS region
    ec2   = boto3.setup_default_session(region_name=region)
    ec2   = boto3.client('ec2')
    zones = ec2.describe_availability_zones()['AvailabilityZones']

    kwargs['REGION']  = region
    kwargs['AZs']     = [z['ZoneName'] for z in zones]
    kwargs['AZcodes'] = [z.split('-')[2] for z in kwargs['AZs']]

    return kwargs


# Assemble all the components of a stack into a single cloudformation::stack object
def assemble(stack, region, args, imports={}):

    kwargs = get_aws_metadata(args.region, kwargs=args.kwargs or {})

    # Create a dictionary to hold all the information
    cfn_stack = { 'AWSTemplateFormatVersion': '2010-09-09' }

    # Section names start with '0'
    sections = [l for l in os.listdir(stack) if l.startswith('0')]
    sections.sort()

    # If importing, process the ImportedResources yaml document
    if imports:
        import_filter = jinjify.process_template('ImportedResources.yml', kwargs)

    for section in sections:
        sec = section.split('_')[1]

        # Create an empty dictionary key for this section for all the files to add their data
        cfn_stack[sec] = {}

        # Traverse the directory hierarchy, parsing all files along the way
        for dirpath, dirs, files in os.walk(os.path.join(stack, section)):
            for f in files:
                # Process each file as a Jinja template first
                contents = jinjify.process_template(os.path.join(dirpath, f), kwargs)
                filename = f.lower()

                if filename.endswith('.yml') or filename.endswith('yaml'):
                    # Process YAML files (most everything)
                    print("Flipping %s" % os.path.relpath(os.path.join(dirpath, f), '.'))

                    # if this is an import template (rare)
                    if sec == 'Resources' and imports:
                        # Only import keys specified in the imported resources file
                        keys = [key for key in contents.keys() if key in import_filter.keys()]
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

    # If this is an import template, then it is not allowed to have an Outputs section
    if imports: cfn_stack.pop('Outputs', None)

    return {k: v for k, v in cfn_stack.items() if v} # discard null/empty keys
