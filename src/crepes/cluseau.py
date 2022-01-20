#!/usr/bin/env python3
# Copyright (c) 2020-2021 Seemant Kulleen <seemantk@gmail.com>

# TODO:
# --force to overwrite an existing dir tree (remove the old one)
# move all this into the crepes binary under an --init flag



import os
from cfn_tools import load_yaml, dump_yaml

# Constants
SECTIONS = ['Description', 'Metadata', 'Parameters', 'Mappings','Conditions', 'Transform', 'Resources', 'Outputs']


#
# Main Function
#
def cluseau(template, destdir):
    if template:
        # Read a YAML CloudFormation template
        with open(template) as f:
            current = load_yaml(f)

    # Create the section directories if they don't exist
    for i, section in enumerate(SECTIONS, start=1):
        # Create a directory for the section of the template, e.g 01_Description/
        secdir = '{}_{}'.format(str(i).zfill(2), section)

        try:
            os.makedirs(os.path.join(destdir, secdir), exist_ok=True)

            if template:
                process_section(secdir, section, current[section], destdir)
            else:
                if(section == 'Description'):
                    process_description('Description of the stack goes here.',secdir, destdir)
        except KeyError:
            continue

# Helper Functions
def process_description(description, secdir, destdir):
    with open(os.path.join(destdir, secdir, 'description.txt'), 'w') as f:
        f.write(description)


def process_resources(resources, secdir, destdir):
    for resname in resources:
        # Grab the AWS resource type (e.g. AWS::EC2::LaunchInstance)
        resource = resources[resname]
        resource_type = resource['Type'].split('::')
        # Bring the 'AWS' part to the front
        resource_type.reverse()
        # Discard the 'AWS' part
        resource_type.pop()
        # Re-reverse the string to make it normal again
        resource_type.reverse()

        # Construct the directory name, e.g. /<destdir>/07_Resources/EC2/
        dirname = os.sep.join([destdir, secdir, os.sep.join(resource_type)])

        # Construct the filename, e.g. LaunchInstance.yml
        filename = '.'.join([resname, 'yml'])

        # Create a directory named for each resource type
        os.makedirs(dirname, exist_ok=True)

        # Write out the object into its own file
        with open(os.path.join(dirname, filename), 'w') as f:
            f.write(dump_yaml({'%s' % resname: resource}))



def process_section(secdir, section, content, destdir):
    print("processing %s" % secdir)
    if(section == 'Description'): # Write out the description file
        process_description(content, secdir , destdir)
    elif(section == 'Resources'):
        process_resources(content, secdir, destdir)
    else:
        destfile = os.path.join(destdir, secdir, '%s.yml' % section.lower())
        with open(destfile, 'w') as f:
            f.write(dump_yaml(content))


if __name__ == "__main__":
    main()
