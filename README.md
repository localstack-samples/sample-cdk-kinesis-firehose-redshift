# CDK deployment of a Kinesis Event Stream to Data Firehose to Redshift data pipeline
LocalStack sample CDK app deploying a Kinesis Event Stream to Data Firehose to Redshift data pipeline, including sample producer and consumer

| Key          | Value                                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------------- |
| Environment  | <img src="https://img.shields.io/badge/LocalStack-deploys-4D29B4.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAKgAAACoABZrFArwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALbSURBVHic7ZpNaxNRFIafczNTGIq0G2M7pXWRlRv3Lusf8AMFEQT3guDWhX9BcC/uFAr1B4igLgSF4EYDtsuQ3M5GYrTaj3Tmui2SpMnM3PlK3m1uzjnPw8xw50MoaNrttl+r1e4CNRv1jTG/+v3+c8dG8TSilHoAPLZVX0RYWlraUbYaJI2IuLZ7KKUWCisgq8wF5D1A3rF+EQyCYPHo6Ghh3BrP8wb1en3f9izDYlVAp9O5EkXRB8dxxl7QBoNBpLW+7fv+a5vzDIvVU0BELhpjJrmaK2NMw+YsIxunUaTZbLrdbveZ1vpmGvWyTOJToNlsuqurq1vAdWPMeSDzwzhJEh0Bp+FTmifzxBZQBXiIKaAq8BBDQJXgYUoBVYOHKQRUER4mFFBVeJhAQJXh4QwBVYeHMQJmAR5GCJgVeBgiYJbg4T8BswYPp+4GW63WwvLy8hZwLcd5TudvBj3+OFBIeA4PD596nvc1iiIrD21qtdr+ysrKR8cY42itCwUP0Gg0+sC27T5qb2/vMunB/0ipTmZxfN//orW+BCwmrGV6vd63BP9P2j9WxGbxbrd7B3g14fLfwFsROUlzBmNM33XdR6Meuxfp5eg54IYxJvXCx8fHL4F3w36blTdDI4/0WREwMnMBeQ+Qd+YC8h4g78wF5D1A3rEqwBiT6q4ubpRSI+ewuhP0PO/NwcHBExHJZZ8PICI/e73ep7z6zzNPwWP1djhuOp3OfRG5kLROFEXv19fXP49bU6TbYQDa7XZDRF6kUUtEtoFb49YUbh/gOM7YbwqnyG4URQ/PWlQ4ASllNwzDzY2NDX3WwioKmBgeqidgKnioloCp4aE6AmLBQzUExIaH8gtIBA/lFrCTFB7KK2AnDMOrSeGhnAJSg4fyCUgVHsolIHV4KI8AK/BQDgHW4KH4AqzCQwEfiIRheKKUAvjuuu7m2tpakPdMmcYYI1rre0EQ1LPo9w82qyNziMdZ3AAAAABJRU5ErkJggg=="> <img src="https://img.shields.io/badge/AWS-deploys-F29100.svg?logo=amazon">                                                                                  |
| Services     | Kinesis Data Stream, Firehose, S3, Redshift                                                          |
| Integrations | CDK                                                                                                  |
| Categories   | BigData                                                                                  |
| Level        | Intermediate                                                                                         |
| GitHub       | [Repository link](https://github.com/localstack-samples/sample-cdk-kinesis-firehose-redshift)        |


![acrhitecture diagram showing the pipeline including producer, kinesis stream, data firehose, s3 bucket, redshift and consumer](architecture-diagram.png)

# Prerequisites

## Required Software
- Python 3.11
- node >16
- Docker
- AWS CLI
- AWS CDK
- LocalStack CLI

<details>
  <summary>if you are on Mac:</summary>

    1. install python@3.11
        
        ```bash
        brew install pyenv
        pyenv install 3.11.0
        ```

    2. install nvm and node >= 16
    
        ```bash
        brew install nvm
        nvm install 20
        nvm use 20
        ```
    3. install docker

        ```bash
        brew install docker
        ```

    4. install aws cli, cdk

        ```bash
        brew install awscli
        npm install -g aws-cdk
        ```

    5. install localstack-cli and cdklocal
        
        ```bash
        brew install localstack/tap/localstack-cli
        npm install -g aws-cdk-local
        ```
</details>


## Setup development environment
Clone the repository and navigate to the project directory.
    
    ```bash
    git clone git@github.com:localstack-samples/sample-cdk-kinesis-firehose-redshift.git
    cd sample-cdk-kinesis-firehose-redshift
    ```

Copy `.env.example` to `.env` and set the environment variables based on your target environment.
You can use the sample user and password and names, or set your own.



Create a virtualenv using python@3.11 and install all the development dependencies there:

```bash
pyenv local 3.11.0
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```    


# Deployment
- Configure the AWS CLI
- Set the environment variables in the .env file based on .env.example

## Deploy the CDK stack manually
Against AWS

- unset the .env variable "AWS_ENDPOINT_URL"
by uncommenting the line in the `.env` file and reloading it.
If you run the debugger, you will also need to uncomment the line in `.vscode/launch.json`
  
```bash
cdk synth
cdk bootstrap
cdk deploy KinesisFirehoseRedshiftStack1
python -m utils/prepare_redshift.py
cdk deploy KinesisFirehoseRedshiftStack2
```

Against LocalStack

- set the .env variable "AWS_ENDPOINT_URL" to "http://localhost:4566"

```bash
localstack start
cdklocal synth
cdklocal bootstrap
cdklocal deploy KinesisFirehoseRedshiftStack1
python -m utils/prepare_redshift.py
cdklocal deploy KinesisFirehoseRedshiftStack2
```

## Deploy the CDK stack using the Makefile
Against AWS

- unset the .env variable "AWS_ENDPOINT_URL" 
by uncommenting the line in the `.env` file and reloading it.
If you run the debugger, you will also need to uncomment the line in `.vscode/launch.json`

```bash
make deploy-aws
```

Against LocalStack

- set the .env variable "AWS_ENDPOINT_URL" to "http://localhost:4566"

```bash
localstack start
make deploy-localstack
```

# Testing

## Run the tests either against AWS or LocalStack
```bash
make test
```

This will run a pytest defined in `tests/test_cdk.py`, put sample data into the Kinesis stream and check if the data is being ingested into the Redshift table.
If you are running the tests against LocalStack, you need to restart the LocalStack container for consecutive runs, since the Redshift table is not being cleaned up after the tests.
The same is true for the AWS deployment, you can manually clean up the Redshift table after the tests, or re-deploy the stack.

## Github Actions CI tests
The github actions workflow defined in `.github/workflows/main.yaml` will install the required dependencies, start a LocalStack containerdeploy the infrastructure aginast LocalStack and run the test.
To set up the workflow, you need to create an environment and set the variables and secrets from you `.env` file.
The workflow will run on every push to the main branch.

# Interact with the deployed resources

## Start sample kinesis producer
set the endpoint url and port acording to your target.
```bash
make start-producer
```
This will run the producer defined in `utils/producer.py` in the background and start sending new data to the kinesis stream, each 10 seconds.

## Read data from Redshift
Open the Jupyter Notebook (simples way if you are on VSCode is using the extension: https://code.visualstudio.com/docs/datascience/jupyter-notebooks) and run the cells to read data from Redshift.
As new data from the mock Kinesis producer is being sent to the Kinesis stream, the data will be automatically ingested into the Redshift table.
You can re-run the cells in the Jupyter Notebook to see the data being updated in real-time.

# Contributing
We appreciate your interest in contributing to our project and are always looking for new ways to improve the developer experience.
We welcome feedback, bug reports, and even feature ideas from the community. Please refer to the contributing file for more details on how to get started.
