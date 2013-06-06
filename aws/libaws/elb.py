from boto.ec2 import elb

from .service import BaseService


class ELBService(BaseService):
    def __init__(self, settings):
        super(ELBService, self).__init__(settings)
        region_name = settings.get('ELB', 'REGION_NAME', None)
        self.conn = elb.connect_to_region(region_name=region_name)
        assert self.conn is not None

    def regions(self, *args, **kwargs):
        return elb.regions(*args, **kwargs)

    def list(self, *args, **kwargs):
        return self.conn.get_all_load_balancers(*args, **kwargs)