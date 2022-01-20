#!/usr/bin/env python3

# Copyright 2020-2022 Seemant Kulleen <seemantk@gmail.com>

import argparse
import stackify, cluseau

def parse_command_line_arguments():
    # Helper to parse keyword arguments for Jinja variables
    class ParseKwargs(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split('=')
                getattr(namespace, self.dest)[key] = value


    # Available command line arguments and their defaults
    parser = argparse.ArgumentParser(
        description='process jinja YAML files and assemble into a CloudFormation template'
    )

    subparser = parser.add_subparsers(dest='command')
    crepes = subparser.add_parser('stack')
    cluseau = subparser.add_parser('unstack')

    # Common arguments
    parser.add_argument(
        'directory',
        help='source directory (Crepes) or destination directory (Cluseau)',
        metavar='dir', type=str
    )

    # Crepes arguments
    crepes.add_argument(
        '--region',
        help='AWS Region',
        dest='region', type=str
    )
    crepes.add_argument(
        '--output',
        help='output CloudFormation YAML file',
        dest='outfile', type=str,
        default='CloudFormation.yml'
    )
    crepes.add_argument(
        '--import',
        help='name of file to output the resources list',
        dest='imports', type=str
    )
    crepes.add_argument(
        '--kwargs',
        help="list of KEY=value pairs",
        dest='kwargs', nargs='*',
        action=ParseKwargs
    )

    # Cluseau arguments
    cluseau.add_argument(
        '--source',
        help='source CloudFormation template',
        dest='template', type=str
    )

    # return the parsed command line arguments
    return parser.parse_args()


#
# Main loop
#
def main():
    args = parse_command_line_arguments()

    if args.command == 'stack':
        stackify.stackify(args.directory, args.region, args.outfile, args.kwargs or {}, args.imports)

    elif args.command == 'unstack':
        cluseau.cluseau(args.template, args.directory)


# Execute if run as a script
if __name__ == "__main__":
    main()
