# rebuild_autoscaling_group
This repo contains a script that will go through the EC2 instances in an AWS autoscaling group, terminate an instance, wait for another healthy instance to replace it, then terminate the next one until all the instances have been terminated and rebuilt.
