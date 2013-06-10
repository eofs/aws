from boto.ec2 import elb

from aws.libaws.service import BaseService


class ELBService(BaseService):
    def __init__(self, settings):
        super(ELBService, self).__init__(settings)
        region_name = settings.get('ELB', 'REGION_NAME', 'us-west-1')
        self.conn = elb.connect_to_region(region_name=region_name)
        assert self.conn is not None

    def regions(self, *args, **kwargs):
        return elb.regions(*args, **kwargs)

    def list(self, names=[], *args, **kwargs):
        return self.conn.get_all_load_balancers(load_balancer_names=names, *args, **kwargs)

    def zones(self, balancer, zone_names, add=True):
        if add:
            return self.conn.enable_availability_zones(balancer, zone_names)
        return self.conn.disable_availability_zones(balancer, zone_names)
