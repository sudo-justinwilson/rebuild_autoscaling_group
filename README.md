# Rebuild an AWS autoscaling cluster

This repo contains a script that will go through the EC2 instances in an AWS autoscaling group, terminate an instance, wait for another healthy instance to replace it, then terminate the next one until all the instances have been terminated and rebuilt.

## Getting Started

Follow the instructions in the _'Installing'_ section to get started with the script.


### Prerequisites

* Python3 should be installed.
* The following pip packages need to be installed: boto, boto3, botocore
* The use of boto assume that AWS credentials are configured. See [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for more information on boto AWS credentials configuration.

```
# Installing the required PIP python packages:
$ pip3 install boto boto3 botocore
```

### Installing

Install this script with the following steps:

Say what the step will be
1) Clone this repository:

```
$ git clone https://github.com/sudo-justinwilson/rebuild_autoscaling_group.git
```


2) Make the script executable:

```
$ chmod -v +x ${/PATH/TO/REPO}/rebuild_asg.py
```


3) Test that the script works:

```
$ ./rebuild_asg.py --help
usage: rebuild_asg.py [-h] [-r REGION] [-n] asg

This script will loop through the instances in an autoscaling group, terminate
an instance, wait for the instance to be replaced, then terminate the next
instance. This will cause the ASG to rebuild all the instances.

positional arguments:
  asg                   The autoscaling group to rebuild

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        To specify which region to query. Note that this is an
                        optional parameter because it may not be needed if you
                        have a default region configured
  -n, --noop            Don't terminate. This flag can be used for testing
```

## Built With

* [Boto](https://boto3.amazonaws.com/v1/documentation/) - Boto package is used for interfacing with AWS

## Contributing

Any bugs or issues should be submitted to the [github repo](https://github.com/sudo-justinwilson/rebuild_autoscaling_group/).

## Authors

* **Justin Wilson** - *Initial work* - [github](https://github.com/sudo-justinwilson)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

