from boto.ec2 import autoscale

from aws.libaws.service import BaseService


class ASService(BaseService):
    def __init__(self, settings):
        super(ASService, self).__init__(settings)
        region_name = settings.get('AS', 'REGION_NAME', 'us-west-1')
        self.conn = autoscale.connect_to_region(region_name=region_name)
        assert self.conn is not None

    def list(self, *args, **kwargs):
        return self.conn.get_all_groups()