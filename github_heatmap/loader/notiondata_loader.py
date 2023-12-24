import json
import time
from collections import defaultdict

import pendulum
import requests

from github_heatmap.loader.base_loader import BaseLoader, LoadError
from github_heatmap.loader.config import NOTION_API_URL, NOTION_API_VERSION


class NotionDataLoader(BaseLoader):
    track_color = "#40C463"
    unit = "hours"

    def __init__(self, from_year, to_year, _type, **kwargs):
        super().__init__(from_year, to_year, _type)
        self.number_by_date_dict = defaultdict(int)
        self.notion_token = kwargs.get("notiondata_token", "")
        self.database_id = kwargs.get("notion_database_id", "")
        self.date_name = kwargs.get("notion_date_name", "Datetime")  # Changed prop_name to date_name
        self.prop_name = kwargs.get("notion_prop_name", "")  # New parameter
        self.filter = kwargs.get("notion_filter", "")  # New parameter
    
    @classmethod
    def add_loader_arguments(cls, parser, optional):
        parser.add_argument(
            "--notiondata_token",
            dest="notiondata_token",
            type=str,
            required=True,  # 如果是必要参数就设置为 True
            help="The Notion token."
        )
        parser.add_argument(
            "--notion_database_id",
            dest="notion_database_id",
            type=str,
            required=True,  # 如果是必要参数就设置为 True
            help="The Notion database id."
        )
        parser.add_argument(
            "--notion_date_name",
            dest="notion_date_name",
            type=str,
            required=False,
            help="The database property name which stores the date."
        )
        parser.add_argument(
            "--notion_prop_name",
            dest="notion_prop_name",
            type=str,
            required=False,
            help="The property to read values from (supported type: formula, number, checkbox)."
        )
        parser.add_argument(
            "--notion_filter",
            dest="notion_filter",
            type=str,
            required=False,
            help="The filter query to apply on the Notion database."
        )


    def get_api_data(self, start_cursor="", page_size=100, data_list=[]):
        if self.filter:
            payload = {
                "page_size": page_size,
                "filter": {'property':self.filter.split('#')[0],'select':{'equals':self.filter.split('#')[1]}}
            }
        else:
            payload = {
                "page_size": page_size,
                #"filter": {'property':'类型','select':{'equals':'每日记录'}}
            }

        if start_cursor:
            payload.update({"start_cursor": start_cursor})

        headers = {
            "Accept": "application/json",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.notion_token,
        }

        resp = requests.post(
            NOTION_API_URL.format(database_id=self.database_id),
            json=payload,
            headers=headers,
        )

        if not resp.ok:
            raise LoadError("Can not get Notion data, please check your config")
        data = resp.json()
        results = data["results"]
        next_cursor = data["next_cursor"]
        data_list.extend(results)
        if not data["has_more"]:
            return data_list
        time.sleep(0.3)
        return self.get_api_data(
            start_cursor=next_cursor, page_size=page_size, data_list=data_list
        )

    def make_track_dict(self):
        data_list = self.get_api_data()
        for result in data_list:
            dt = result["properties"][self.date_name]["date"]["start"]
            date_str = pendulum.parse(dt).to_date_string()
            if self.prop_name:
                prop_type = result["properties"][self.prop_name]['type']
                if prop_type == 'formula':
                    value = result["properties"][self.prop_name]["formula"]["number"]
                elif prop_type == 'number':
                    value = result["properties"][self.prop_name]["number"]
                elif prop_type == 'checkbox':
                    value = 1 if result["properties"][self.prop_name]["checkbox"] else 0
                self.number_by_date_dict[date_str] = value if value else 0
            else:
                self.number_by_date_dict[date_str] += 1  # count times
            
        for _, v in self.number_by_date_dict.items():
            self.number_list.append(v)

    def get_all_track_data(self):
        self.make_track_dict()
        self.make_special_number()
        return self.number_by_date_dict, self.year_list
