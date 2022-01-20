#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

from cfn_tools import dump_json

def importify(stack, outfile):
    # Create list of resources. This is required when using the AWS CLI to deploy CloudFormation stacks
    # The command is `aws create-changeset --resources-to-import file://{outfile}`
    imports = [_create_res_list_item(res, stack['Resources'][res]) for res in stack['Resources']]

    with open(outfile, 'w') as f:
        f.write(dump_json(imports))


# Internal Helper function which creates items for a resource list, as required if using the awscli
def _create_res_list_item(resource, obj):
    obj['DeletionPolicy'] = 'Retain'

    temp = {}
    try:
        for prop in imports[resource]['Property']:
            print('Importing %s for %s' % (prop, resource))
            temp[prop] = obj['Properties'][prop]
    except KeyError:
    # e.g. SNSTopic requires TopicARN for import, but it is not a property in the template
        pass

    # Replace the Properties key with only the filtered items
    obj['Properties'] = temp

    return {
        'ResourceType': obj['Type'],
        'LogicalResourceId': resource,
        'ResourceIdentifier': imports[resource]['Matcher']
    }
