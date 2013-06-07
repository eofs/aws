Utility program for Amazon Web Services
=======================================

**Features**

* Wrapper for [Boto](http://boto.readthedocs.org/) and [Fabric](http://docs.fabfile.org/)
* List instances and regions for ELB and EC2 services
* List EC2 instances for specific ELB
* Run Fabric tasks against all EC2 instances or for EC2 instances for specific ELB

**Motivation**

It's possible to specify target hosts inside your Fabric files dynamically or statically. Modifying list of hosts would require you to modify your code directly. I didn't like that so I created a tool to easily define list of target machines for your tasks.

**TODO**

* More features!
* Start/Stop/Terminate instances
* Manage your AMIs
* AWS Auto Scaling support

#Installation#

```bash
$ pip install aws
```

#Configuration#

`aws` should work with minimal configuration.

You only need to make sure that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables are set.

If you want to use Fabric and execute code on your remote servers, or use different regions, you can set necessary info into settings file:

```ini
# /home/<username>/.aws/settings.conf
[SSH]
KEY_FILE = /home/<username>/.ec2/myserver.pem
USER = ubuntu

# Service specific settings
[EC2]
REGION = 'eu-west-1'

# Service specific settings
[ELB]
REGION = 'eu-west-1'
```


See [Boto's](http://boto.readthedocs.org/) documentation for more how to set Amazon access credentials: http://boto.readthedocs.org/en/latest/boto_config_tut.html

See [Fabric's](http://docs.fabfile.org/) documentation on how to set SSH access credentials: http://docs.fabfile.org/en/latest/usage/execution.html#leveraging-native-ssh-config-files

#Usage#

List all ELB instances:
```bash
$ aws elb list
```

List all EC2 instances:
```bash
$ aws ec2 list
```

List all EC2 instances for ELB named "MyBalancer":
```bash
$ aws ec2 list --elb MyBalancer
```

Run Fabric tasks against EC2 instances:
```bash
$ aws ec2 fab mymethod
```

Run Fabric tasks against EC2 instances and define fabfile to be used:
```bash
$ aws ec2 fab mymethod -f myfabfile.py
```

You can pass parameters to your methods as with Fabric's `fab` command:
```bash
$ aws ec2 fab mymethod:name='Jeff'
```

Or run Fabric tasks against only EC2 instances inside ELB:
```bash
$ aws ec2 fab mymethod --elb MyBalancer
```
