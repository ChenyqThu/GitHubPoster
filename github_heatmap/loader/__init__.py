from github_heatmap.loader.apple_health_loader import AppleHealthLoader
from github_heatmap.loader.bbdc_loader import BBDCLoader
from github_heatmap.loader.bilibili_loader import BilibiliLoader
from github_heatmap.loader.chatgpt_loader import ChatGPTLoader
from github_heatmap.loader.cichang_loader import CiChangLoader
from github_heatmap.loader.covid_loader import CovidLoader
from github_heatmap.loader.dota2_loader import Dota2Loader
from github_heatmap.loader.duolingo_loader import DuolingoLoader
from github_heatmap.loader.forest_loader import ForestLoader
from github_heatmap.loader.from_github_issue_loader import GitHubIssuesLoader
from github_heatmap.loader.garmin_loader import GarminLoader
from github_heatmap.loader.github_loader import GitHubLoader
from github_heatmap.loader.gitlab_loader import GitLabLoader
from github_heatmap.loader.gpx_loader import GPXLoader
from github_heatmap.loader.jike_loader import JikeLoader
from github_heatmap.loader.json_loader import JsonLoader
from github_heatmap.loader.kindle_loader import KindleLoader
from github_heatmap.loader.leetcode_loader import LeetcodeLoader
from github_heatmap.loader.multiple_loader import MultipleLoader
from github_heatmap.loader.neodb_loader import NeoDBLoader
from github_heatmap.loader.notion_loader import NotionLoader
from github_heatmap.loader.notiondata_loader import NotionDataLoader
from github_heatmap.loader.nrc_loader import NRCLoader
from github_heatmap.loader.ns_loader import NSLoader
from github_heatmap.loader.openlanguage_loader import OpenLanguageLoader
from github_heatmap.loader.shanbay_loader import ShanBayLoader
from github_heatmap.loader.strava_loader import StravaLoader
from github_heatmap.loader.summary_loader import SummaryLoader
from github_heatmap.loader.todoist_loader import TodoistLoader
from github_heatmap.loader.wakatime_loader import WakaTimeLoader
from github_heatmap.loader.weread_loader import WereadLoader
from github_heatmap.loader.youtube_loader import YouTubeLoader

LOADER_DICT = {
    "apple_health": AppleHealthLoader,
    "bbdc": BBDCLoader,
    "duolingo": DuolingoLoader,
    "shanbay": ShanBayLoader,
    "strava": StravaLoader,
    "cichang": CiChangLoader,
    "ns": NSLoader,
    "gpx": GPXLoader,
    "issue": GitHubIssuesLoader,
    "leetcode": LeetcodeLoader,
    "youtube": YouTubeLoader,
    "bilibili": BilibiliLoader,
    "github": GitHubLoader,
    "gitlab": GitLabLoader,
    "kindle": KindleLoader,
    "wakatime": WakaTimeLoader,
    "dota2": Dota2Loader,
    "multiple": MultipleLoader,
    "nike": NRCLoader,
    "notion": NotionLoader,
    "notiondata":NotionDataLoader,
    "garmin": GarminLoader,
    "forest": ForestLoader,
    "json": JsonLoader,
    "jike": JikeLoader,
    "summary": SummaryLoader,
    "weread": WereadLoader,
    "covid": CovidLoader,
    "todoist": TodoistLoader,
    "openlanguage": OpenLanguageLoader,
    "chatgpt": ChatGPTLoader,
    "neodb": NeoDBLoader,
}

__all__ = (
    "AppleHealthLoader",
    "BilibiliLoader",
    "CiChangLoader",
    "Dota2Loader",
    "DuolingoLoader",
    "GitHubIssuesLoader",
    "GitHubLoader",
    "GitLabLoader",
    "GPXLoader",
    "KindleLoader",
    "LeetcodeLoader",
    "NSLoader",
    "ShanBayLoader",
    "StravaLoader",
    "WakaTimeLoader",
    "YouTubeLoader",
    "MultipleLoader",
    "NotionLoader",
    "NotionDataLoader",
    "NRCLoader",
    "LOADER_DICT",
    "ForestLoader",
    "GarminLoader",
    "JsonLoader",
    "JikeLoader",
    "SummaryLoader",
    "BBDCLoader",
    "WereadLoader",
    "CovidLoader",
    "TodoistLoader",
    "OpenLanguageLoader",
    "ChatGPTLoader",
    "NeoDBLoader",
)
