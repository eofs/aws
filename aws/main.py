#!/bin/env python

import argparse
import getpass

from fabric import api as fab
from fabric import state as fab_state
from fabric.main import find_fabfile, load_fabfile, parse_arguments

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
    instance_ids = args.instances
    instances = service.list(elb=args.elb, instance_ids=instance_ids)
    hosts = service.resolve_hosts(instances)

    fab.env.hosts = hosts
    fab.env.key_filename = settings.get('SSH', 'KEY_FILE')
    fab.env.user = settings.get('SSH', 'USER', getpass.getuser())
    fab.env.parallel = True

    fabfile = find_fabfile(args.file)
    if not fabfile:
        print 'Couldn\'t find any fabfiles!'
        return

    fab.env.real_fabile = fabfile
    docstring, callables, default = load_fabfile(fabfile)
    fab_state.commands.update(callables)

    commands_to_run = parse_arguments(args.methods)
    for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
        fab.execute(name,
                    hosts=arg_hosts,
                    roles=arg_roles,
                    exclude_hosts=arg_exclude_hosts,
                    *args, **kwargs)


def ec2_list_handler(parser, args):
    service = EC2Service(settings)
    if 'regions' == args.type:
        list_regions(service)
    else:
        instance_ids = args.instances
        reservations = service.list(elb=args.elb, instance_ids=instance_ids)
        for r in reservations:
            for i in r.instances:
                state = ('       ' if i.state == 'stopped' else i.state)
                print '[%s] [%s] [%s] %s:\t%s' % (state, i.instance_type, i.id, i.key_name, i.dns_name)


def ec2_fab_handler(parser, args):
    service = EC2Service(settings)
    ec2_fab(service, args)


def elb_list_handler(parser, args):
    service = ELBService(settings)
    if 'regions' == args.type:
        list_regions(service)
    else:
        for b in service.list():
            print '%s: %s' % (b.name, b.dns_name)


def main():
    """
    AWS support script's main method
    """
    p = argparse.ArgumentParser(description='Manage Amazon AWS services',
                                prog='aws',
                                version=__version__)
    subparsers = p.add_subparsers(help='Select Amazon AWS service to use')

    # Elastic Cloud Computing
    ec2_service = subparsers.add_parser('ec2', help='Amazon Elastic Compute Cloud')
    ec2_subparsers = ec2_service.add_subparsers(help='Perform action')

    ec2_service_list = ec2_subparsers.add_parser('list', help='List items')
    ec2_service_list.add_argument('--elb', '-e', help='Filter instances inside this ELB instance')
    ec2_service_list.add_argument('--instances', '-i', nargs='*', metavar=('id', 'id'),
                                 help='List of instance IDs to use as filter')
    ec2_service_list.add_argument('--type', default='instances', choices=['instances', 'regions'],
                                  help='List items of this type')
    ec2_service_list.set_defaults(func=ec2_list_handler)

    ec2_service_fab = ec2_subparsers.add_parser('fab', help='Run Fabric commands')
    ec2_service_fab.add_argument('--elb', '-e', help='Run against EC2 instances for this ELB')
    ec2_service_fab.add_argument('--instances', '-i', nargs='*', metavar=('id', 'id'),
                                 help='List of instance IDs to use as filter')
    ec2_service_fab.add_argument('--file', '-f', nargs='+', help='Define fabfile to use')
    ec2_service_fab.add_argument('methods',
                                 metavar='method:arg1,arg2=val2,host=foo,hosts=\'h1;h2\',',
                                 nargs='+',
                                 help='Run Fabric tasks in EC2 instances. You can pass multiple arguments for your fabfile.')
    ec2_service_fab.set_defaults(func=ec2_fab_handler)

    # ec2_service_start = ec2_subparsers.add_parser('start', help='Start instance')
    # ec2_service_stop = ec2_subparsers.add_parser('stop', help='Stop instance')
    # ec2_service_terminate = ec2_subparsers.add_parser('terminate', help='Terminate instance')

    # Elastic Load Balancing
    elb_service = subparsers.add_parser('elb', help='Amazon Elastic Load Balancing')
    elb_subparsers = elb_service.add_subparsers(help='Perform action')

    elb_service_list = elb_subparsers.add_parser('list', help='List items')
    elb_service_list.add_argument('--type', default='balancers', choices=['balancers', 'regions'],
                                  help='List items of this type')
    elb_service_list.set_defaults(func=elb_list_handler)

    # elb_service_create = elb_subparsers.add_parser('create', help='Create new Load Balancer')
    # elb_service_delete = elb_subparsers.add_parser('delete', help='Delete Load Balancer')
    # elb_service_register = elb_subparsers.add_parser('register', help='Register EC2 instance')
    # elb_service_zone = elb_subparsers.add_parser('zone', help='Enable or disable region')

    arguments = p.parse_args()
    arguments.func(p, arguments)


if __name__ == '__main__':
    main()