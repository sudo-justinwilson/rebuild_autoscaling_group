#!/usr/bin/python

from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2 import autoscale
import boto
import boto3
import time
import argparse


class RebuildASG:
    """
    "This script will loop through the instances in an autoscaling group, terminate an instance, wait for the instance to be replaced, then terminate the next instance. This will cause the ASG to rebuild all the instances."
    Instantiate an object.
    """
    def __init__(self, asg, region = False):
        self.asg = asg          # string: name of ASG
        self.region = region    # string: name of region
        self.instances = self.get_asg_instances()
        self._count = len(self.instances)
        self.autoscaling_group = self.get_asg_object()
        self.desired_capacity = self.autoscaling_group.desired_capacity

    def get_connection(self):
        """
        Returns a boto.ec2.autoscale.AutoScaleConnection object which allows us to connect to AWS.
        """
        if self.region:
            conn = boto.ec2.autoscale.connect_to_region(self.region)   
        else:
            conn = AutoScaleConnection()
        return conn

    def get_asg_instances(self):
        """
        Returns ASG in the form of:
            [
                Instance<id:i-03170a4777f9b10cf, state:InService, health:HEALTHY group:autoscaling_ecs-autoscaling-group>,
                 Instance<id:i-08a2cff9b8cd167bb, state:InService, health:HEALTHY group:autoscaling_ecs-autoscaling-group>
            ]
        This is a list of boto.ec2.autoscale.instance.Instance instance objects.
        """
        instances = [i for i in self.get_connection().get_all_autoscaling_instances() if i.group_name == self.asg]
        return instances

    def get_asg_object(self):
        """
        Returns an boto.ec2.autoscale.group.AutoScalingGroup ASG object.
        """
        asg = self.get_connection().get_all_groups(names=[self.asg])
        if len(asg) == 0:
            raise Exception("We couldn't find an autoscaling group with the name '{asg}' in the {region} region".format(asg = self.asg, region = self.get_connection().region))
        elif len(asg) > 1:
            raise Exception("The API call returned more than one autoscaling groups with the name '{asg}' in the {region} region".format(asg = self.asg, region = self.get_connection().region))
        else:
            return asg[0]

    def get_ec2_object(self, instance_id):
        """
        This method returns an boto3.resources.factory.ec2.Instance EC2 instance object.

        :Params:
            :instance_id:
                The EC2 instance ID in the form of a string.
        """
        try:
            ec2 = boto3.resource('ec2')
            ec2instance = ec2.Instance(instance_id)

            # make sure that this EC2 instance exists:
            print("The {instance_id} EC2 instance is {state}".format(instance_id = instance_id, state = ec2instance.state['Name']))
            return ec2instance
        except Exception as e:
            print("We can't seem to get an EC2 instance by the name of {instance}.".format(instance = instance_id))
            raise e

    def main(self):
        try:
            if self._count == 0:
                raise Exception("There doesn't seem to be any instances in this ASG?")
            for instance in self.instances:
                print("Now looping over instance {0}".format(instance.instance_id))

                # make EC2 object:
                ec2instance = self.get_ec2_object(instance.instance_id)
                print('terminating {0}'.format(instance.instance_id))

                # terminate EC2 instance:
                terminate_response = ec2instance.terminate()

                if terminate_response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print("The terminate HTTP code was {0}".format(terminate_response['ResponseMetadata']['HTTPStatusCode']))

                    # wait for this instance to be removed from asg:
                    while instance.instance_id in [x.instance_id for x in self.get_asg_instances() if x.health_status.upper() == 'HEALTHY']:
                        print("The same instance id ({id}) is still in the healthy instance ids".format(id = instance.instance_id))
                        time.sleep(20)
                    print("THE ID HAS BEEN REMOVED!!")

                    # wait until the desired count has been achieved:
                    while len([x.instance_id for x in self.get_asg_instances() if x.health_status.upper() == 'HEALTHY']) < self._count:
                        print("Waiting for the desired count to reach 'HEALTHY' status..")
                        time.sleep(20)

                    print("THE desired_count has been reached. We will now wait for the instances to reach the 'InService' state..")
                    while len([x.instance_id for x in self.get_asg_instances() if x.lifecycle_state == 'InService']) < self._count:
                        print("Waiting for the desired count to reach 'InService' state..")
                        time.sleep(20)
                else:
                    raise Exception('The terminate_response HTTP status was not 200!!')
                print("COMPLETE! {0} instances have been terminated and replaced.".format(self._count))
        except Exception as e:
            raise e

if __name__ == '__main__':
    #--------   ADD CLI ARGS:
    parser = argparse.ArgumentParser(description="This script will loop through the instances in an autoscaling group, terminate an instance, wait for the instance to be replaced, then terminate the next instance. This will cause the ASG to rebuild all the instances.")
    parser.add_argument("asg", help="The autoscaling group to rebuild")
    parser.add_argument("-r", "--region", help="To specify which region to query. Note that this is an optional parameter because it may not be needed if you have a default region configured")
    parser.add_argument("-n", "--noop", help="Don't terminate. This flag can be used for testing", action="store_true")

    args = parser.parse_args()
    ASG = args.asg
    region = args.region
    noop = args.noop

    #--------   INITIALIZE OBJECT:
    rebuildasg = RebuildASG(ASG, region=region)
    if noop:
        print("The ASG named {ASG} has {count} active instances".format(ASG=rebuildasg.asg, count = rebuildasg._count))
    else:
        # check if the desired capacity is running:
        if rebuildasg._count != rebuildasg.desired_capacity:
            message = """WARNING!!!
There are currently {0} active instances in the {1} autoscaling group. 
That means that the autoscaling group is not currently running at the desired_capacity.
This script will terminate one at a time and wait for a new instance to be launched.

Are you sure that you want to proceed? [only 'yes' will proceed]    """.format(rebuildasg._count, rebuildasg.asg)
            answer = input(message)
            if answer == 'yes':
                rebuildasg.main()
            else:
                print("Aborting..")
        else:
            print("There are currently {instances} out of {desired} instances running in the {asg} autoscaling group. Proceeding with rebuild of autoscaling group...".format(instances = rebuildasg._count, desired = rebuildasg.desired_capacity, asg = rebuildasg.asg))
            rebuildasg.main()
