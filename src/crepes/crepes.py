#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

import os, argparse
import stackify

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


#
# Main loop
#
def main():
    args = parse_command_line_arguments()

    # Create the destination dir, if it doesn't exist
    outdir = os.path.dirname(os.path.abspath(args.outfile))
    os.makedirs(outdir, exist_ok=True)

    # Assemble the stack into a dict and convert that to YAML 
    stack = stackify.assemble(args.directory, args.region, args.kwargs or {}, imports=args.imports)

    # Output the stack file and the import resources list file (if any)
    stackify.create_stack_files(stack, args.imports, args.outfile)


# Execute if run as a script
if __name__ == "__main__":
    main()
