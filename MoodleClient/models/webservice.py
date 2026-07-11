from pydantic import BaseModel, HttpUrl, RootModel

from .common import MoodleRawHttpUrl
from .enums import Homepage


# Belongs to SiteInfo
class Function(BaseModel):
    name: str
    version: str


# Belongs to SiteInfo
class AdvancedFeature(BaseModel):
    name: str
    value: (
        bool | int
    )  # The Moodle source code says "Usually 1 means enabled." which doesn't quite spark a lot of confidence


# https://github.com/moodle/moodle/blob/MOODLE_502_STABLE/public/webservice/externallib.php#L240
# MOODLE_502_STABLE get_site_info_returns
class SiteInfo(BaseModel):
    sitename: str
    username: str
    firstname: str
    lastname: str
    fullname: str
    lang: str
    userid: int
    siteurl: HttpUrl
    userpictureurl: HttpUrl
    functions: list[Function]
    downloadfiles: bool | None = None
    uploadfiles: bool | None = None
    release: str | None = None
    version: str | None = None
    mobilecssurl: MoodleRawHttpUrl = None
    advancedfeatures: list[AdvancedFeature] | None = None
    usercanmanageownfiles: bool | None = None
    userquota: int | None = None  # 0 = ignore quota
    usermaxuploadfilesize: int | None = None  # -1 = ignore file size restriction
    userhomepage: Homepage | None = None
    userhomepageurl: HttpUrl | None = None
    userprivateaccesskey: str | None = None
    siteid: int | None = None
    sitecalendartype: str | None = None
    usercalendartype: str | None = None
    userissiteadmin: bool | None = None
    theme: str | None = None
    limitconcurrentlogins: int | None = None
    usersessionscount: int | None = None
    policyagreed: bool | None = None
    usercanchangeconfig: bool | None = None
    usercanviewconfig: bool | None = None
    sitesecret: str | None = None


# Here to follow the styleguide while separating SiteInfo from the return Structure
class GetSiteInfoStructure(SiteInfo):
    pass
