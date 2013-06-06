Utility program for Amazon Web Services
=======================================

**Features**

* List instances and regions for ELB and EC2 services
* List EC2 instances for specific ELB
* Run Fabric tasks against all EC2 instances or for EC2 instances for specific ELB

#Installation#

```bash
$ pip install aws
```

#Usage#

List all ELB instances
```bash
$ aws elb --list
```

List all EC2 instances
```bash
$ aws ec2 --list
```

List all EC2 in ELB named "MyBalancer"
```bash
$ aws ec2 --list --elb MyBalancer
```

Run Fabric tasks against EC2 instances
```bash
$ aws ec2 --fab myfabfile mymethod
```

You can pass parameters to your methods as with `fab` command
```bash
$ aws ec2 --fab myfabfile mymethod:name='Jeff'
```

Or run Fabric tasks against only EC2 instances inside ELB
```bash
$ aws ec2 --elb MyBalancer --fab myfabfile mymethod
```
