# crepes
tl;dr: instead of editing massive CloudFormation files, edit small yaml files arranged in diretories that suit your organization prefernce.

This project was inspired by [grapes](https://github.com/0x4447/0x4447-cli-node-grapes), an excellent tool written in Node.js. I love using CloudFormation templates. I had the same needs as [they did](https://github.com/0x4447/0x4447-cli-node-grapes/blob/development/README.md#-grapes), and using that tool opened up some interesting possbilities in my mind.
If I was halfway competent in node, I would have submitted pull requests directly to grapes.  But I'm more comfortable in python, so I created this tool to address some of the needs I had as an AWS Architect and DevOps consultant.

Firstly, I wanted to use YAML files rather than JSON. I find YAML much easier to understand. Also, YAML files are smaller than equivalent JSON files.

Secondly, I wanted to be able to create a base template which can be stretched or shrunk at deployment time to match the target region.  In CloudFormation there isn't (yet) a way to specify "I want one EC2 instance per Availabilty Zone, which would mean 4 in Ohio (us-east-2), 6 in Virginia (us-east-1) and 2 in Northern California (us-west-1).  By using Jinja to loop through the AZs variable (built-in) we can do just that.

You can also define your own custom Jinja variables and pass then to crepes.

Regarding the name: I find YAML to be much easier and less cluttered than JSON. Since YAML files are smaller than the equivalent JSON file, I called this tool crepes while still honoring the name 'grapes'.


## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Directory Structure](#directory-structure)
4. [Template Components](#template-components)
5. [Jinja Variables](#jinja-variables)
6. [Examples](#examples)
7. [Advanced Features](#advanced-features)
8. [Contributing](#contributing)
9. [License](#license)


## Installation
### Dependencies/Requirements

These will get pulled in if you install this package using pip.

* install and configure [boto3](https://github.com/boto/boto3)
* install [jinja2](https://pypi.org/project/Jinja2/)
* install [cfn-flip](https://github.com/awslabs/aws-cfn-template-flip)

### Install Crepes
run:
```python setup.py install```


Or install directly from PyPI:
pip install


## Usage
Initialize an empty directory structure, ready to populate with yaml files:
```
crepes.py unstack /destination/path/to/deconstructed-template
```

Deconstruct a CloudFormation template into a directory structure:
```
crepes.py unstack --source CloudFormation.yml /directory/for/deconstructed-template
```

Stack a directory of YAML files into a CloudFormation template ready to deploy to AWS:
```
crepes.py stack --region $REGION --output CloudFormation.yml /directory/of/deconstructed-template
```

### Walkthrough

The crepes tool works by organizing CloudFormation templates into a directory structure of YAML files.
Each section of a CloudFormation template (Description, Parameters, Resources, etc.) is stored in its
own file, making it easy to manage and version control.


#### Directory Structure

When you use crepes, it creates a directory structure like this:


```
template-directory/
├── Description.yaml
├── Metadata.yaml
├── Parameters.yaml
├── Mappings.yaml
├── Conditions.yaml
├── Transform.yaml
├── Resources/
│   ├── ec2-instance.yaml
│   ├── s3-bucket.yaml
│   └── vpc.yaml
└── Outputs.yaml
```

Each file contains the corresponding CloudFormation section content in YAML format.


#### Template Components
Each component of a CloudFormation template can be stored in its own YAML file:

##### Description
The Description file contains the template description:
```
Description: "My CloudFormation template description"
```


##### Metadata
The Metadata file contains metadata about the template:

```
Metadata:
  AWS::CloudFormation::Designer:
    Group: MyGroup
```

##### Parameters
The Parameters file contains parameter definitions:

```
Parameters:
  InstanceType:
    Type: String
    Default: t2.micro
    Description: EC2 instance type
```

#####  Mappings

The Mappings file contains mapping definitions:

```
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345678
    us-west-2:
      AMI: ami-87654321
```


##### Conditions
The Conditions file contains condition definitions:

```
Conditions:
  IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
```

##### Transform

The Transform file contains transform definitions:

```
Transform: AWS::Include
```

##### Resources

The Resources directory contains individual resource files:

```
# Resources/ec2-instance.yaml
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      InstanceType: !Ref InstanceType
```

##### Outputs

The Outputs file contains output definitions:

```
Outputs:
  InstanceId:
    Description: Instance ID of the newly created EC2 instance
    Value: !Ref MyEC2Instance
```


##### Jinja Variables
Crepes supports Jinja templating to make templates more dynamic:

##### Built-in Variables

Crepes provides built-in variables that can be used in templates:

 * AWS::Region - The AWS region
 * AWS::AccountId - The AWS account ID
 * AWS::StackName - The CloudFormation stack name

##### Custom Variables

You can pass custom variables to crepes:

```
crepes.py stack --region us-east-1 --output template.yaml --var environment=production --var
version=1.0 /path/to/template
```


##### Example Usage

```
# Resources/ec2-instance.yaml
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      InstanceType: !Ref InstanceType
      Tags:
        - Key: Environment
          Value: "{{ environment }}"
        - Key: Version
          Value: "{{ version }}"
```


### Examples

#### Simple Example
Create a basic template structure:


```
mkdir my-template
cd my-template
crepes.py unstack .
```


#### Complex Example with Variables

Create a template that uses region-specific configurations:

```
crepes.py stack --region us-east-1 --output template.yaml --var environment=production --var
version=1.0 /path/to/template
```


### Advanced Features

#### Import Functionality

Crepes supports importing other templates:

```
# Resources/imported-resources.yaml
Resources:
  ImportedResource:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateUrl: https://s3.amazonaws.com/bucket/template.yaml
```

#### Conditional Resources

Use conditions to create resources only in specific regions:

```
# Resources/conditional-resources.yaml
Conditions:
  IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]

Resources:
  EC2InstanceInUsEast1:
    Condition: IsUsEast1
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-12345678
      InstanceType: t2.micro
```

#### Multi-Region Deployment

Deploy the same template to multiple regions:

```
for region in us-east-1 us-west-2 eu-west-1; do
  crepes.py stack --region $region --output "template-$region.yaml" /path/to/template
done
```


## Contributing

Contributions are welcome! Please follow these steps:
 1. Fork the repository
 2. Create a feature branch
 3. Make your changes
 4. Add tests if applicable
 5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
