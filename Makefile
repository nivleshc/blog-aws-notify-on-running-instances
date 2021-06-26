#define variables
aws_profile = ${AWS_PROFILE_NAME}
aws_s3_bucket = ${AWS_S3_BUCKET_NAME}
aws_s3_bucket_prefix = monitor-ec2-instances
aws_stack_name = monitor-ec2-instances
aws_stack_iam_capabilities = CAPABILITY_IAM
sam_package_template_file = template.yaml
sam_package_output_template_file = package.yaml

all: usage
.PHONY: all

usage:
	@echo make package - package the sam application and copy it to the s3 bucket [s3://${aws_s3_bucket}/${aws_s3_bucket_prefix}/]
	@echo make deploy  - deploy the packaged sam application to AWS
	@echo make update  - package the sam application and then deploy it to AWS
	@echo make validate - validate template file [${sam_package_template_file}]
	@echo make clean   - delete local package.yml file
.PHONY: usage

package:
	sam package --template-file ${sam_package_template_file} --output-template-file ${sam_package_output_template_file} --s3-bucket ${aws_s3_bucket} --s3-prefix ${aws_s3_bucket_prefix} --profile ${aws_profile}
.PHONY: package

deploy:
	sam deploy --template-file ${sam_package_output_template_file} --stack-name ${aws_stack_name} --capabilities ${aws_stack_iam_capabilities} --profile ${aws_profile} --parameter-overrides ParameterKey=SlackWebhookURL,ParameterValue=${SLACK_WEBHOOK_URL}
.PHONY: deploy

update:
	make clean
	make package
	make deploy
.PHONY: update

validate:
	sam validate --template-file ${sam_package_template_file}
.PHONY: validate

clean:
	rm -f ./${sam_package_output_template_file}
.PHONY: clean