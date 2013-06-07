Utility program for Amazon Web Services
=======================================

**Features**

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

#Usage#

List all ELB instances:
```bash
$ aws elb list
```

List all EC2 instances:
```bash
$ aws ec2 list
```

List all EC2 in ELB named "MyBalancer":
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

You can pass parameters to your methods as with `fab` command:
```bash
$ aws ec2 fab mymethod:name='Jeff'
```

Or run Fabric tasks against only EC2 instances inside ELB:
```bash
$ aws ec2 fab --elb MyBalancer mymethod
```
