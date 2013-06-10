#!/bin/env python

import argparse
import prettytable
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


def elb_table(balancers):
    """
    Print nice looking table of information from list of load balancers
    """
    t = prettytable.PrettyTable(['Name', 'DNS', 'Ports', 'Zones', 'Created'])
    t.align = 'l'
    for b in balancers:
        ports = ['%s: %s -> %s' % (l[2], l[0], l[1]) for l in b.listeners]
        ports = '\n'.join(ports)
        zones = '\n'.join(b.availability_zones)
        t.add_row([b.name, b.dns_name, ports, zones, b.created_time])
    return t


def ec2_table(instances):
    """
    Print nice looking table of information from list of instances
    """
    t = prettytable.PrettyTable(['ID', 'State', 'Type', 'Name', 'DNS'])
    t.align = 'l'
    for i in instances:
        t.add_row([i.id, i.state, i.instance_type, i.key_name, i.dns_name])
    return t


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
        instance_list = []
        for r in reservations:
            instance_list.extend(r.instances)
        print ec2_table(instance_list)


def ec2_create_handler(parser, args):
    pass


def ec2_start_handler(parser, args):
    service = EC2Service(settings)
    instance_ids = args.instance
    instances = service.start(instance_ids)
    print ec2_table(instances)


def ec2_stop_handler(parser, args):
    service = EC2Service(settings)
    instance_ids = args.instance
    instances = service.stop(instance_ids, args.force)
    print ec2_table(instances)


def ec2_terminate_handler(parser, args):
    service = EC2Service(settings)
    instance_ids = args.instance
    instances = service.terminate(instance_ids)
    print ec2_table(instances)


def ec2_fab_handler(parser, args):
    service = EC2Service(settings)
    ec2_fab(service, args)


def elb_list_handler(parser, args):
    service = ELBService(settings)
    if 'regions' == args.type:
        list_regions(service)
    else:
        print elb_table(service.list())


def elb_zones_handler(parser, args):
    service = ELBService(settings)
    balancer = args.balancer
    zone_names = args.zone
    add = True
    if 'disable' == args.status:
        add = False

    try:
        zones = service.zones(balancer, zone_names, add)
    except AttributeError:
        # Remote this try/except after https://github.com/boto/boto/pull/1492
        # is merged into master.
        pass

    print elb_table(service.list(names=[balancer]))


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
                                 help='Specify one or more methods to execute.')
    ec2_service_fab.set_defaults(func=ec2_fab_handler)

    ec2_service_create = ec2_subparsers.add_parser('create', help='Create and start new instances')
    ec2_service_create.set_defaults(func=ec2_create_handler)

    ec2_service_start = ec2_subparsers.add_parser('start', help='Start existing instances')
    ec2_service_start.add_argument('instance', nargs='+', help='ID of an instance to start')
    ec2_service_start.set_defaults(func=ec2_start_handler)

    ec2_service_stop = ec2_subparsers.add_parser('stop', help='Stop instances')
    ec2_service_stop.add_argument('instance', nargs='+', help='ID of an instance to stop')
    ec2_service_stop.add_argument('--force', '-f', action='store_true', help='Force stop')
    ec2_service_stop.set_defaults(func=ec2_stop_handler)

    ec2_service_terminate = ec2_subparsers.add_parser('terminate', help='Terminate instances')
    ec2_service_terminate.add_argument('instance', nargs='+', help='ID of an instance to terminate')
    ec2_service_terminate.set_defaults(func=ec2_terminate_handler)

    # Elastic Load Balancing
    elb_service = subparsers.add_parser('elb', help='Amazon Elastic Load Balancing')
    elb_subparsers = elb_service.add_subparsers(help='Perform action')

    elb_service_list = elb_subparsers.add_parser('list', help='List items')
    elb_service_list.add_argument('--type', default='balancers', choices=['balancers', 'regions'],
                                  help='List items of this type')
    elb_service_list.set_defaults(func=elb_list_handler)

    elb_service_zones = elb_subparsers.add_parser('zones', help='Enable or disable zone')
    elb_service_zones.add_argument('balancer', help='Name of the load balancer')
    elb_service_zones.add_argument('zone', nargs='+', help='Name of the zone')
    elb_service_zones.add_argument('status', help='Disable of enable zones', choices=['enable', 'disable'])
    elb_service_zones.set_defaults(func=elb_zones_handler)

    # elb_service_create = elb_subparsers.add_parser('create', help='Create new Load Balancer')
    # elb_service_delete = elb_subparsers.add_parser('delete', help='Delete Load Balancer')
    # elb_service_register = elb_subparsers.add_parser('register', help='Register EC2 instance')
    # elb_service_zone = elb_subparsers.add_parser('zone', help='Enable or disable region')

    arguments = p.parse_args()
    arguments.func(p, arguments)


if __name__ == '__main__':
    main()