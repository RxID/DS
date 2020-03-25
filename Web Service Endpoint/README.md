# DS Backend Module  setup for deployment to AWS

includes CORS and HTTPS functionality

## AWS Elastic Beanstalk Deployment

### Create AWS Keypair

### Create New EB Environment
    Choose Instance Size
    Add KeyPair
    Choose Python image
    Deploy sample app

### Deploy non-SSL version of app
    Setup file structure
    review .ebextensions/config.ssl  file
    create new timestamped zipfile ( Do not use already uploaded zipfiles)

### Test SSH access
    ssh -i "AWSkeypair.pem" ec2-user@ec2-18-220-146-205.us-east-2.compute.amazonaws.com  (ec2 instance url)