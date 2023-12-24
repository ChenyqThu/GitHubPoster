"""Create a poster from track data."""
from collections import defaultdict

import svgwrite
import math
from datetime import date, timedelta

from github_heatmap.structures import XY, ValueRange


class Poster:
    def __init__(self):
        self.title = None
        self.tracks = {}
        self.type_list = []
        self.loader_list = []
        self.length_range_by_date = ValueRange()
        self.length_range_by_date_dict = defaultdict(ValueRange)
        self.units = "metric"
        self.colors = {
            "background": "#222222",
            "text": "#FFFFFF",
            "special": "#FFFF00",
            "track": "#4DD2FF",
        }
        self.width = 200
        self.height = 300
        self.years = None
        # maybe support more type
        self.tracks_drawer = None
        self.trans = None
        self.with_animation = False
        self.with_statistics = False
        self.animation_time = 10
        self.year_tracks_date_count_dict = defaultdict(int)
        self.year_tracks_type_dict = defaultdict(dict)

        # for year summary
        self.is_summary = False

    def set_tracks(self, tracks, years, type_list):
        self.type_list.extend(type_list)
        self.tracks = tracks
        self.years = years
        # for multiple types...
        # TODO maybe refactor another class later
        for date, num in tracks.items():
            self.year_tracks_date_count_dict[date[:4]] += 1
            if type(num) is dict:
                for k, v in num.items():
                    self.length_range_by_date_dict[k].extend(v)
            else:
                self.length_range_by_date.extend(num)
        for t in type_list:
            self.compute_track_statistics(t)

    @property
    def is_multiple_type(self):
        return len(self.type_list) > 1

    def set_with_statistics(self, with_statistics):
        self.with_statistics = with_statistics

    def set_with_animation(self, with_animation):
        self.with_animation = with_animation

    def set_animation_time(self, animation_time):
        self.animation_time = animation_time

    def draw(self, drawer, output):
        assert self.type_list, "type_list is empty"
        if drawer.name == "circular":
            self._draw_circular(drawer, output)
        else:
            self._draw_github(drawer, output)

    def _draw_circular(self, drawer, output):
        self.tracks_drawer = drawer
        d = svgwrite.Drawing(output, (f"{self.width}mm", f"{self.height}mm"))
        d.viewbox(0, 0, self.width, self.height)
        d.add(d.rect((0, 0), (self.width, self.height), fill=self.colors["background"]))
        self.__draw_tracks(d, XY(100, 100))
        d.save()

    def _draw_github(self, drawer, output):
        height = self.height
        width = self.width
        self.tracks_drawer = drawer
        d = svgwrite.Drawing(output, (f"{width}mm", f"{height}mm"))
        d.viewbox(0, 0, self.width, height)
        d.add(d.rect((0, 0), (width, height), fill=self.colors["background"]))
        self.__draw_header(d)
        self.__draw_tracks(d, XY(10, 14))
        # for multiple types show
        if self.is_multiple_type:
            self.__draw_footer(d)
        d.save()

    def __draw_tracks(self, d, offset):
        self.tracks_drawer.draw(d, offset, self.is_summary)

    def __draw_header(self, d):
        text_color = self.colors["text"]
        title_style = "font-size:6px; font-family:Arial; font-weight:bold;"
        d.add(d.text(self.title, insert=(10, 10), fill=text_color, style=title_style))

    def __draw_footer(self, d):
        self.tracks_drawer.draw_footer(d)
    
    def compute_track_statistics(self, t):
        total_sum_year_dict = defaultdict(lambda: {"total": 0, "count": 0, "average": 0.0, 
                                                "longest_streak": 0, "current_streak": 0, 
                                                "values": [], "standard_deviation": 0.0,"max":0.0,"min":1000.0})
        
        # 确保按日期升序遍历
        for year in self.years:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)

            current_date = start_date
            while current_date <= end_date:
                str_date = current_date.strftime("%Y-%m-%d")
                num = self.tracks.get(str_date, {t: 0})
                value = num.get(t, 0) if isinstance(num, dict) else num  # 此处进行了修改
                total_sum_year_dict[year]["total"] += value
                if value > 0:
                    total_sum_year_dict[year]["values"].append(value)
                    total_sum_year_dict[year]["count"] += 1
                    total_sum_year_dict[year]["current_streak"] += 1
                    if total_sum_year_dict[year]["current_streak"] > total_sum_year_dict[year]["longest_streak"]:
                        total_sum_year_dict[year]["longest_streak"] = total_sum_year_dict[year]["current_streak"]
                    if value > total_sum_year_dict[year]["max"]:  # Update max duration
                        total_sum_year_dict[year]["max"] = value
                    if value < total_sum_year_dict[year]["min"]:  # Update min duration
                        total_sum_year_dict[year]["min"] = value
                else:
                    total_sum_year_dict[year]["current_streak"] = 0
                current_date += timedelta(days=1)

            # 计算平均值和标准差
            for year, data in total_sum_year_dict.items():
                data['max'] = round(data['max'],2)
                data['min'] = round(data['min'],2)
                count = data["count"]
                values = data["values"]
                total = data["total"]
                average = total / count if count else 0
                data["average"] = round(average, 2)
                variance = sum((x - average) ** 2 for x in values) / count if count else 0
                data["standard_deviation"] = round(math.sqrt(variance), 2)

        self.total_sum_year_dict = total_sum_year_dict
        return total_sum_year_dict