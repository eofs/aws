#!/bin/env python

import argparse
import getpass

from fabric import api as fab
from fabric.main import parse_arguments

from aws import __version__
from libaws.conf import settings
from libaws.ec2 import EC2Service
from libaws.elb import ELBService


def list_regions(service):
    """
    List regions for the service
    """
    for region in service.regions():
        print '%(name)s: %(endpoint)s' % {
            'name': region.name,
            'endpoint': region.endpoint,
        }

def ec2_fab(service, args):
    """
    Run Fabric commands against EC2 instances
    """
    instances = service.list(args.elb)
    hosts = service.resolve_hosts(instances)

    fab.env.hosts = hosts
    fab.env.key_filename = settings.get('SSH', 'KEY_FILE')
    fab.env.user = settings.get('SSH', 'USER', getpass.getuser())
    fab.env.parallel = True

    def import_file(file):
        return __import__(file)

    module_name = args.fab[0]
    module = import_file(module_name)

    commands_to_run = parse_arguments(args.fab[1:])
    for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
        method = getattr(module, name, None)
        if method is not None:
            fab.execute(method,
                        hosts=arg_hosts,
                        roles=arg_roles,
                        exclude_hosts=arg_exclude_hosts,
                        *args, **kwargs
            )

def ec2_service_handler(parser, args):
    service = EC2Service(settings)
    if args.list:
        list = service.list(elb=args.elb)
        for x in list:
            for i in x.instances:
                state = ('       ' if i.state == 'stopped' else i.state)
                print '[%s] [%s] [%s] %s:\t%s' % (state, i.instance_type, i.id, i.key_name, i.dns_name)
    elif args.regions:
        list_regions(service)
    elif args.fab:
        if len(args.fab) < 2:
            parser.error('Not enough parameters provided for --fab.')
        ec2_fab(service, args)

def elb_service_handler(parser, args):
    service = ELBService(settings)
    if args.list:
        for x in service.list():
            print '%s: %s' % (x.name, x.dns_name)
    elif args.regions:
        list_regions(service)

def main():
    """
    AWS support script's main method
    """
    p = argparse.ArgumentParser(description='Manage Amazon AWS services',
                                prog='aws',
                                version=__version__)
    subparsers = p.add_subparsers(help='Select Amazon AWS service to use')

    ec2_service = subparsers.add_parser('ec2', help='Amazon EC2')
    ec2_service.add_argument('--list', '-l', action='store_true', help='List instances')
    ec2_service.add_argument('--regions', '-r', action='store_true', help='List regions')
    ec2_service.add_argument('--elb', '-e', help='Filter instances inside this ELB instance')
    ec2_service.add_argument('--fab', '-f', nargs='+', metavar=('fabfile method', ':arg1,arg2=val2,host=foo,hosts=\'h1;h2\','),
                             help='Run Fabric tasks in EC2 instances. You can pass multiple arguments for your fabfile.')
    ec2_service.set_defaults(func=ec2_service_handler)

    elb_service = subparsers.add_parser('elb', help='Amazon Elastic Load Balancer')
    elb_service.add_argument('--list', '-l', action='store_true', help='List load balancers')
    elb_service.add_argument('--regions', '-r', action='store_true', help='List regions')
    elb_service.set_defaults(func=elb_service_handler)

    arguments = p.parse_args()
    arguments.func(p, arguments)

if __name__ == '__main__':
    main()