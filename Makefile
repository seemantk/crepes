# Makefile for deploying CloudFormation templates with crepes

# Variables
AWS_REGION ?= us-east-1
TEMPLATE_DIR ?= templates
OUTPUT_FILE ?= CloudFormation.yml
IMPORT_FILE ?= imports.json
AWS_PROFILE ?= default

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  deploy        - Deploy template to AWS"
	@echo "  build         - Build CloudFormation template"
	@echo "  clean         - Remove generated files"
	@echo "  help          - Show this help"

# Build the CloudFormation template
.PHONY: build
build:
	@echo "Building CloudFormation template for region $(AWS_REGION)"
	crepes stack $(TEMPLATE_DIR) --region $(AWS_REGION) --output $(OUTPUT_FILE) --import $(IMPORT_FILE)

# Deploy to AWS
.PHONY: deploy
deploy: build
	@echo "Deploying template to AWS region $(AWS_REGION)"
	aws cloudformation deploy \
		--template-file $(OUTPUT_FILE) \
		--stack-name $(shell basename $(TEMPLATE_DIR)) \
		--region $(AWS_REGION) \
		--profile $(AWS_PROFILE) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

# Deploy with resource import (if imports file exists)
.PHONY: deploy-import
deploy-import: build
	@echo "Deploying template with resource import"
	aws cloudformation create-change-set \
		--stack-name $(shell basename $(TEMPLATE_DIR)) \
		--change-set-name $(shell basename $(TEMPLATE_DIR))-import \
		--template-body file://$(OUTPUT_FILE) \
		--resources-to-import file://$(IMPORT_FILE) \
		--region $(AWS_REGION) \
		--profile $(AWS_PROFILE)

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files"
	rm -f $(OUTPUT_FILE) $(IMPORT_FILE)

# Validate template
.PHONY: validate
validate: build
	@echo "Validating CloudFormation template"
	aws cloudformation validate-template --template-body file://$(OUTPUT_FILE) --region $(AWS_REGION) --profile $(AWS_PROFILE)

# Show help
.PHONY: help
help:
	@echo "CloudFormation Deployment Makefile"
	@echo "Usage: make [target] [AWS_REGION=us-east-1] [TEMPLATE_DIR=templates]"
	@echo ""
	@echo "Targets:"
	@echo "  build         - Build CloudFormation template"
	@echo "  deploy        - Deploy template to AWS"
	@echo "  deploy-import - Deploy with resource import"
	@echo "  validate      - Validate template"
	@echo "  clean         - Remove generated files"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Environment variables:"
	@echo "  AWS_REGION    - AWS region (default: us-east-1)"
	@echo "  TEMPLATE_DIR  - Template directory (default: templates)"
	@echo "  OUTPUT_FILE   - Output file (default: CloudFormation.yml)"
	@echo "  IMPORT_FILE   - Import file (default: imports.json)"
	@echo "  AWS_PROFILE   - AWS profile (default: default)"
