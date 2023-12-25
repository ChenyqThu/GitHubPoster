import calendar
import datetime

import svgwrite.animate

from github_heatmap.config import (
    COLOR_TUPLE,
    DEFAULT_DOM_COLOR,
    DOM_BOX_DICT,
    DOM_BOX_TUPLE,
    MONTH_NAMES,
)
from github_heatmap.err import BaseDrawError
from github_heatmap.utils import interpolate_color, make_key_times


class Drawer:
    name = "github"

    def __init__(self, p):
        self.poster = p
        self.year_size = 80 * 5.0 / 80.0
        self.year_style = f"font-size:{self.year_size}px; font-family:Arial;font-weight:bold;"
        self.year_length_style = f"font-size:{80 * 4.0 / 80.0}px; font-family:Arial;"
        self.month_names_style = "font-size:2.5px; font-family:Arial"

    @property
    def type_color_dict(self):
        """
        for multiple types
        """
        return dict(
            zip(self.poster.type_list, COLOR_TUPLE[: len(self.poster.type_list)])
        )

    def make_color(self, length_range, length):
        sp2 = self.poster.special_number.get("special_number2")
        sp1 = self.poster.special_number.get("special_number1")
        has_special = False
        if sp2 and sp1 and length:
            has_special = sp2 < length < sp1
        color_from = (
            self.poster.colors["special"]
            if has_special
            else self.poster.colors["track"]
        )
        color_to = self.poster.colors["special2"]
        diff = length_range.diameter()
        if diff == 0:
            return color_from

        return interpolate_color(
            color_from, color_to, (length - length_range.lower()) / diff
        )

    def __add_animation(self, rect, key_times, animate_index):
        values = (
            ";".join(["0"] * animate_index)
            + ";"
            + ";".join(["1"] * (len(key_times) - animate_index))
        )
        rect.add(
            svgwrite.animate.Animate(
                "opacity",
                dur=f"{self.poster.animation_time}s",
                values=values,
                keyTimes=";".join(key_times),
                repeatCount="1",
            )
        )
        return rect

    def _gen_day_box(
        self,
        dr,
        rect_x,
        rect_y,
        date_title,
        day_tracks,
        with_animation,
        key_times,
        animate_index,
    ):
        color = self.poster.colors.get("dom")
        if day_tracks:
            color = self.make_color(self.poster.length_range_by_date, day_tracks)
            if day_tracks >= self.poster.special_number["special_number1"]:
                color = self.poster.colors.get("special2") or self.poster.colors.get(
                    "special"
                )
            date_title = f"{date_title} {day_tracks} {self.poster.units}"
        rect = dr.rect((rect_x, rect_y), DOM_BOX_TUPLE, fill=color,rx=0.4, ry=0.4)
        if with_animation:
            rect = self.__add_animation(rect, key_times, animate_index)
        rect.set_desc(title=date_title)
        yield rect

    def _gen_day_boxes(
        self,
        dr,
        rect_x,
        rect_y,
        date_title,
        day_tracks,
        with_animation,
        key_times,
        animate_index,
    ):
        """
        max len(boxes) == 3 like douban see #7
        yield rect1, rect2, rect3
        or
        yield rect1, rect2
        or
        yield rect
        """
        if day_tracks:
            types_len = len(day_tracks)
            dom_tuple = DOM_BOX_DICT.get(types_len).get("dom")
            index = 0
            for _type in self.poster.type_list:
                num = day_tracks.get(_type, 0)
                length_range = self.poster.length_range_by_date_dict.get(_type, 1)
                if not num:
                    continue
                dom = dom_tuple[index]
                color = self.make_color(length_range, num)
                rect = dr.rect((rect_x, rect_y), dom, fill=color,rx=0.4, ry=0.4)
                date_title = f"{date_title} {num} for {_type}"
                if with_animation:
                    rect = self.__add_animation(rect, key_times, animate_index)
                rect.set_desc(title=date_title)
                yield rect
                rect_y += dom_tuple[index][1]
                index += 1
        else:
            rect = dr.rect((rect_x, rect_y), DOM_BOX_TUPLE, fill=DEFAULT_DOM_COLOR)
            if with_animation:
                rect = self.__add_animation(rect, key_times, animate_index)
            yield rect

    # noinspection PyArgumentList
    def _draw_one_calendar(self, dr, year, offset, _type=None):
        start_date_weekday, _ = calendar.monthrange(year, 1)
        github_rect_first_day = datetime.date(year, 1, 1)
        # GitHub profile the first day start from the last Monday of the last year
        # or the first Monday of this year.
        # It depends on if the first day of this year is Monday or not.
        github_rect_day = github_rect_first_day + datetime.timedelta(
            -start_date_weekday
        )

        year_data = self.poster.total_sum_year_dict.get(year, {})
        year_length = year_data.get("total", 0)
        year_average = year_data.get("average", 0.0)
        year_max = year_data.get("max",0.0)
        year_min = year_data.get("min",0.0)
        year_standard_deviation = year_data.get("standard_deviation", 0.0)
        year_longest_streak = year_data.get("longest_streak", 0)
        year_count_days = year_data.get("count", 0)
        year_units = self.poster.units
        if self.poster.units == "mins":
            year_length = int(year_length / 60)
            year_average = round(year_average / 60, 2)  # 保留两位小数
            year_max = round(year_max / 60, 2)
            year_min = round(year_min / 60, 2)
            year_standard_deviation = round(year_standard_deviation / 60, 2)  # 保留两位小数
            year_units = "hours"
        year_units = "小时" if year_units=="hours" else year_units
        year_length = str(int(year_length)) + f" {year_units}"
        year_average_str = f"{year_average} {year_units}（🔺{year_max} 🔻{year_min} ）"
        year_standard_deviation_str = f"{year_standard_deviation} {year_units}"

        dr.add(
            dr.text(
                f"{year}" if _type is None else f"{_type}",
                insert=offset.tuple(),
                fill=self.poster.colors["text"],
                dominant_baseline="hanging",
                style=self.year_style,
            )
        )

        if not self.poster.is_multiple_type and not self.poster.with_statistics:
            dr.add(
                dr.text(
                    f"{year_length}",
                    insert=(offset.tuple()[0] + 165, offset.tuple()[1]),
                    fill=self.poster.colors["text"],
                    dominant_baseline="hanging",
                    style=self.year_length_style,
                )
            )
        # add month name up to the poster one by one
        # because of svg text auto trim the spaces.
        for num, name in enumerate(MONTH_NAMES):
            dr.add(
                dr.text(
                    f"{name}",
                    insert=(offset.tuple()[0] + 15.5 * num, offset.tuple()[1] + self.year_size +4),
                    fill=self.poster.colors["text"],
                    style=self.month_names_style,
                )
            )

        rect_x = 10.0
        animate_index = 1
        year_count, key_times = 0, ""
        if self.poster.with_animation:
            # set default count 10
            year_count = self.poster.year_tracks_date_count_dict.get(str(year), 10)
            key_times = make_key_times(year_count)

        # add every day of this year for 53 weeks and per week has 7 days
        for _ in range(54):
            rect_y = offset.y + self.year_size + 2
            for _ in range(7):
                if int(github_rect_day.year) > year:
                    break
                rect_y += 3.5
                date_title = str(github_rect_day)
                day_tracks = None
                if date_title in self.poster.tracks:
                    day_tracks = self.poster.tracks[date_title]

                    # tricky for may cause animate error
                    if animate_index < len(key_times) - 1:
                        animate_index += 1
                gen_box_func = (
                    self._gen_day_box
                    if len(self.poster.type_list) == 1
                    else self._gen_day_boxes
                )
                for rect in gen_box_func(
                    dr,
                    rect_x,
                    rect_y,
                    date_title,
                    day_tracks,
                    self.poster.with_animation,
                    key_times,
                    animate_index,
                ):
                    dr.add(rect)
                github_rect_day += datetime.timedelta(1)
            rect_x += 3.5
        offset.y += 3.5 * 9 + self.year_size + 1.0

        if self.poster.with_statistics:
            #补充统计数值
            unit = "时长" if year_units == "时长" else year_units
            font_size = 4
            # 定义样式
            label_style = f"font-size:{font_size}px; font-family:Arial; fill:grey"  # 标签样式为灰色
            value_style = f"font-size:{font_size}px; font-family:Arial; font-weight:bold"  # 值样式加粗

            stat_texts = [
                {"label": f"🔷总天数：", "value": f"{year_count_days}天"},
                {"label": f"🔶总{unit}：", "value": f"{year_length}"},
                {"label": f"🔹平均{unit}：", "value": f"{year_average_str}"},
                {"label": f"🔸标准差：", "value": f"{year_standard_deviation_str}"},
                {"label": f"🔥最长连续天数：", "value": f"{year_longest_streak}天"}
            ]
            
            stat_y_offset = offset.y + 3
            for stat in stat_texts:
                label_width = len(stat["label"]) * font_size
                dr.add(dr.text(stat["label"], insert=(10, stat_y_offset), style=label_style))
                dr.add(dr.text(stat["value"], insert=(10 + label_width, stat_y_offset), style=value_style))
                stat_y_offset += 6  # 调整行间距

            # 更新 offset.y
            offset.y += len(stat_texts) * 6 + 3

    def draw(self, dr, offset, is_summary=False):
        if self.poster.tracks is None:
            raise BaseDrawError("No tracks to draw")

        if is_summary:
            for loader in self.poster.loader_list:
                tracks, years = loader.get_all_track_data()
                self.poster.set_tracks(tracks, years, [])
                self.poster.type_list = ["summary"]
                self.poster.special_number = {
                    "special_number1": loader.special_number1,
                    "special_number2": loader.special_number2,
                }
                self.poster.colors["track"] = loader.track_color or "#4DD2FF"
                self.poster.units = loader.unit
                self.poster.compute_track_statistics([loader._type])
                self._draw_one_calendar(dr, years[0], offset, _type=loader._type)
        else:
            for year in range(self.poster.years[0], self.poster.years[-1] + 1)[::-1]:
                self._draw_one_calendar(dr, year, offset)
        print(f"{str(self.poster.type_list)} poster drawer done in `OUT_FOLDER`")

    def draw_footer(self, dr):
        text_color = self.poster.colors["text"]
        header_style = "font-size:4px; font-family:Arial"
        x = 10
        y = self.poster.height - 2.5
        index = 0
        for _type in self.poster.type_list:
            dr.add(dr.rect((x, y - 2.5), DOM_BOX_TUPLE, fill=COLOR_TUPLE[index][0]))
            dr.add(
                dr.text(
                    f": {_type}",
                    insert=(x + 3, y),
                    fill=text_color,
                    style=header_style,
                )
            )
            x += 20
            index += 1
