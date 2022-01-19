# crepes
Easily create dynamic and consistent AWS CloudFormation templates.

This project was inspired by [grapes](https://github.com/0x4447/0x4447-cli-node-grapes), an excellent tool written in Node.js. Please read their README and then return. tl;dr: instead of editing massive CloudFormation files, edit small yaml files arragned in diretories that suit your organization prefernce. I wrote this to help me do client work as an AWS Architect and DevOps Consultant during the past couple of years.

For me, however, JSON is hard to parse.  I find YAML to be much easier and less cluttered than JSON. Since YAML files are smaller than the equivalent JSON file, I called this tool crepes while still honoring the spiritual root project's 'grapes'.

## Description




##Installation
### Requirements
* install and configure [boto3](https://github.com/boto/boto3)
* install [jinja2](https://pypi.org/project/Jinja2/)
* install [cfn-flip](https://github.com/awslabs/aws-cfn-template-flip)

