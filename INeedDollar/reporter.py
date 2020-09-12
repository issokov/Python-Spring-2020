import re
import pandas as pd
from random import choice
from random import randint
from random import uniform
from bisect import bisect_left
from itertools import accumulate
from collections import Counter, defaultdict

from rate_stealer import RateStealer


class TextGenerator:
    def __init__(self, is_title_else_text=True, context_size=5, variability_prob=1/3, top_words_size=7):

        self.rate = RateStealer()
        self.model = defaultdict(Counter)
        self.context_size = context_size
        self.variability_prob = variability_prob
        self.top_words_size = top_words_size
        self.start_tokens_list = [f"^START_{i}" for i in range(self.context_size)]
        self.terminate = "$END$"
        self.go_down_keys = ["упал", "упали", "опустил", "опустился", "понизил", "ниже",
                            "снизил", "понизился", "снизился", "подешевел", "понижен",
                             "рухнул", "обвалился", "дотянул"]
        self.go_up_keys = ["вырос", "превысил", "поднял", "поднялся", "увеличился", "повысился",
                           "подскочил", "перевалил", "выше", "повысил", "повысился", "взлетел", "преодолел"]

        data = pd.read_csv("target_news.csv", encoding="utf-8")
        news = data['title' if is_title_else_text else 'text'].to_numpy()
        dates = data['date'].to_numpy()
        news = list(map(lambda x: self.start_tokens_list + x.split() + [self.terminate], news))
        for one, date in zip(news, dates):
            yyyy, mm, dd = int(date[:4]), int(date[5:7]), int(date[8:10])
            keys = self._get_keys(dd, mm, yyyy)
            template = self._get_template(one, date)
            update_candidates = []
            for i in range(len(template) - self.context_size):
                keys_context = tuple(keys + [template[i + c] for c in range(self.context_size)])
                update_candidates.append((keys_context, template[i + self.context_size]))
                target = template[i + self.context_size]
                if 'доллар' in target or "$USD" in target:
                    keys[0] = True
                if 'евро' in target or "$EURO" in target:
                    keys[1] = True
                if target in self.go_down_keys:
                    if keys[2] == 1:  # Информация о курсе противоречива
                        update_candidates = [] # Значит новость не учитываем
                        break
                    keys[2] = -1
                if target in self.go_up_keys:
                    if keys[2] == -1:
                        update_candidates = []
                        break
                    keys[2] = 1
            for key, cand in update_candidates:
                self.model[key].update([cand])

    def _get_keys(self, dd, mm, yyyy):
        today_usd_rate = self.rate.get_cbr_rate(True, dd, mm, yyyy)
        yesterday_usd_rate = self.rate.get_cbr_rate(True, dd - 1, mm, yyyy)
        usd_go_up = today_usd_rate > yesterday_usd_rate
        today_euro_rate = self.rate.get_cbr_rate(False, dd, mm, yyyy)
        yesterday_euro_rate = self.rate.get_cbr_rate(False, dd - 1, mm, yyyy)
        euro_go_up = today_euro_rate > yesterday_euro_rate
        rate_direction = -1 + euro_go_up + usd_go_up
        return [False, False, rate_direction]

    def _get_template(self, text, date):
        new_text = text.copy()
        for i in range(len(new_text)):
            converted = re.match(r'^-?\d+(?:\.\d+)?$', new_text[i].replace(",", "."))
            yyyy, mm, dd = int(date[:4]), int(date[5:7]), int(date[8:10])
            usd_rate = float(self.rate.get_cbr_rate(True, dd, mm, yyyy))
            euro_rate = float(self.rate.get_cbr_rate(False, dd, mm, yyyy))
            if any(month in new_text[i] for month in ["январ", "феврал", "март", "апрел", "май", "мае", "мая" "июн",
                                                      "июл", "август", "сентябр", "октябр", "ноябр", "декабр"]):
                new_text[i] = '{month}'
                if i and new_text[i - 1] == '{some_const}':
                    new_text[i - 1] = '{some_month_day}'
            if converted is not None:
                value = float(new_text[i].replace(",", "."))
                if i + 1 != len(new_text) and ('копе' in new_text[i + 1] or 'цент' in new_text[i + 1]):
                    new_text[i] = '{penny}'
                elif abs(value - usd_rate) < 5 and 'руб' in new_text[i + 1]:
                    new_text[i] = '{usd}'
                elif abs(value - euro_rate) < 5 and 'руб' in new_text[i + 1]:
                    new_text[i] = '{euro}'
                elif 1998 < value < 2030:
                    new_text[i] = '{year}'
                elif new_text[i] == str(int(dd)):  # Remove first zero if it have
                    new_text[i] = '{today}'
                else:
                    new_text[i] = '{some_const}'
        return new_text

    def _weighted_random(self, pairs):
        sums = list(accumulate(map(lambda x: x[1], pairs)))
        target = randint(0, sums[-1])
        index = bisect_left(sums, target)
        return pairs[index][0]

    def create_template(self, dd, mm, yyyy):
        while True:
            text = self.start_tokens_list.copy()
            keys = self._get_keys(dd, mm, yyyy)
            while text[-1] != self.terminate:
                keys_context = tuple(keys + [text[i] for i in range(-self.context_size, 0)])
                candidates = self.model[keys_context].most_common(self.top_words_size)
                if len(text) <= self.context_size + 1 and uniform(0, 1) > self.variability_prob:
                    text.append(self._weighted_random(candidates))
                else:
                    text.append(choice(candidates)[0])
                if 'доллар' in text[-1]:
                    keys[0] = True
                elif 'евро' in text[-1]:
                    keys[1] = True

            if '{usd}' in text or '{euro}' in text or '{penny}' in text:
                return " ".join(text[self.context_size:-1])

    def generate_text(self, dd, mm, yyyy):
        usd = self.rate.get_cbr_rate(True, dd, mm, yyyy)[:5]
        euro = self.rate.get_cbr_rate(False, dd, mm, yyyy)[:5]
        yesterday_usd = self.rate.get_cbr_rate(True, dd - 1, mm, yyyy)
        yesterday_euro = self.rate.get_cbr_rate(False, dd - 1, mm, yyyy)
        penny_usd = 100 * abs(float(usd) - float(yesterday_usd))
        penny_euro = 100 * abs(float(euro) - float(yesterday_euro))
        template = self.create_template(dd, mm, yyyy)
        while 'доллар' in template and 'евро' in template and 'копе' in template:
            template = self.create_template(dd, mm, yyyy)
        curr_month = ['января', 'февраля', ' марта', 'апреля', 'мая', 'июня',
                      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'][int(mm) - 1]
        context_penny = int(penny_usd if '{usd}' in template else penny_euro)
        new_one = template.format(euro=euro, usd=usd, penny=context_penny, year=str(yyyy),
                               month=curr_month, today=str(dd), some_const=7, some_month_day=13)
        return new_one


class Reporter():

    title_context_size = 3
    title_variability_prob = 1/3
    text_context_size = 4
    text_variability_prob = 1/4

    def __init__(self):
        self.title_generator = TextGenerator(is_title_else_text=True, context_size=self.title_context_size,
                                         variability_prob=self.title_variability_prob)
        self.text_generator = TextGenerator(is_title_else_text=False, context_size=self.text_context_size,
                                        variability_prob=self.text_variability_prob)

    def generate_title(self, dd, mm, yyyy, number=1):
        result = set()
        while len(result) != number:
            result.add(self.title_generator.generate_text(dd, mm, yyyy))
        return result

    def generate_text(self, dd, mm, yyyy, number=1):
        result = set()
        while len(result) != number:
            result.add(self.text_generator.generate_text(dd, mm, yyyy))
        return result

reporter = Reporter()
for new in reporter.generate_title(number=10, dd=26, mm=3, yyyy=2020):
   print(new)
