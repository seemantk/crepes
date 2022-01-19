# crepes
tl;dr: instead of editing massive CloudFormation files, edit small yaml files arragned in diretories that suit your organization prefernce.

This project was inspired by [grapes](https://github.com/0x4447/0x4447-cli-node-grapes), an excellent tool written in Node.js. I love using CloudFormation templates. I had the same needs as [they did](https://github.com/0x4447/0x4447-cli-node-grapes/blob/development/README.md#-grapes), and using that tool opened up some interesting possbilities in my mind.
If I was halfway competent in node, I would have submitted pull requests directly to grapes.  But I'm more comfortable in python, so I created this tool to address some of the needs I had as an AWS Architect and DevOps consultant.

Firstly, I wanted to use TAML files rather than JSON. I find YAML much easier to understand. Also, YAML files are smaller than equivalent JSON files.

Secondly, I wanted to be able to create a base template which can be stretched or shrunk at deployment time to match the target region.  In CloudFormation there isn't (yet) a way to specify "I want one EC2 instance per Availabilty Zone, which would mean 4 in Ohio (us-east-2), 6 in Virginia (us-east-1) and 2 in Northern California (us-west-1).  By using Jinja to loop through the AZs variable (built-in) we can do just that.

You can also define your own custom Jinja variables and pass then to crepes.

Regarding the name: I find YAML to be much easier and less cluttered than JSON. Since YAML files are smaller than the equivalent JSON file, I called this tool crepes while still honoring the name 'grapes'.


## Installation
### Requirements

Use your package manager or homebrew or pip.

* install and configure [boto3](https://github.com/boto/boto3)
* install [jinja2](https://pypi.org/project/Jinja2/)
* install [cfn-flip](https://github.com/awslabs/aws-cfn-template-flip)

## Usage
To initialize an empty directory structure, ready to populate with yaml files:
```
cluseau.py /destination/path/to/deconstructed-template
```

To construct a CloudFormation template ready to deploy to AWS:
```
crepes.py --region $REGION --output CloudFormation.yml /directory/of/deconstructed-template
```

To deconstruct a CloudFormation template into a directory structure:
```
cluseau.py --source CloudFormation.yml /directory/for/deconstructed-template
```
