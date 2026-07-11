from ..models.webservice import GetSiteInfoStructure
from .base import BaseService


class WebServiceService(BaseService):
    # https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/webservice/externallib.php#L240
    # MOODLE_502_STABLE get_site_info_parameters
    async def get_site_info(self) -> GetSiteInfoStructure:
        response = await self.session.request("core_webservice_get_site_info")
        return self._parse_response(response, GetSiteInfoStructure)
