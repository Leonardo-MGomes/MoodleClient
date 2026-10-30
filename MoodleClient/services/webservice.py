from ..models.webservice import GetSiteInfoStructure
from .base import BaseService, moodle_endpoint


class WebServiceService(BaseService):
    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/webservice/externallib.php#L240
    # MOODLE_502_STABLE get_site_info_parameters
    @moodle_endpoint
    async def get_site_info(self) -> GetSiteInfoStructure:
        ...
