#!/usr/bin/python3

from bs4 import BeautifulSoup
import json
import os
import re
import urllib.parse

class Column:
    def name(self):
        return self.__class__.__name__

    def weight(self):
        return 1


class Name(Column):
    def weight(self):
        return ''

    def signal(self):
        return ''

    def value(self, soup):
        return soup.find(class_='infobox_name').text


class Address(Column):
    def weight(self):
        return ''

    def signal(self):
        return ''

    def value(self, soup):
        return soup.find(text='London').next_sibling.next_sibling


class AtCapacity(Column):
    def weight(self):
        return 0

    def signal(self):
        return 1

    def value(self, soup):
        return re.sub(r'At ([0-9]+)% Capacity.*', r'\1%', soup.find(id='capacity').text)


class Year(Column):
    def __init__(self, year, num_years):
        self.year_ = year
        self.num_years_ = num_years

    def weight(self):
        return (self.year_ + 1) / self.num_years_

    def name(self):
        return str(self.year_) + ' ' + super().name()


class TextFieldYearMultiplier(Year):
    def __init__(self, name, signal, year, num_years, multiplier, offset):
        super().__init__(year, num_years)
        self.name_ = name
        self.signal_ = signal
        self.year_ = year
        self.multiplier_ = multiplier
        self.offset_ = offset

    def name(self):
        return str(self.year_) + ' ' + str(self.offset_) + ' ' + self.name_

    def signal(self):
        return self.signal_

    def value(self, soup):
        tag = soup.find_all(text=self.name_)
        if not tag:
            return ''
        index = self.year_ * self.multiplier_ + self.offset_
        if index >= len(tag):
            return ''
        return tag[index].parent.next_sibling.text


class TextFieldYear(TextFieldYearMultiplier):
    def __init__(self, name, signal, year, num_years):
        super().__init__(name, signal, year, num_years, 1, 0)

    def name(self):
        return str(self.year_) + ' ' + self.name_


class TextField(TextFieldYear):
    def __init__(self, name, signal):
        super().__init__(name, signal, 0, 1)

    def name(self):
        return self.name_


def find_outcome(soup):
    for outcome in soup.find_all(class_='infobox_report_outcome'):
        if not str.isspace(outcome.text):
            return outcome


class OfstedYear(Column):
    def signal(self):
        return 1

    def value(self, soup):
        return find_outcome(soup).parent.previous_sibling.previous_sibling.text.split()[2]


class OfstedRating(Column):
    def signal(self):
        return 1

    def value(self, soup):
        outcome = find_outcome(soup).text
        if outcome == 'Outstanding':
            return 3
        if outcome == 'Good':
            return 2
        if outcome == 'Satisfactory':
            return 1
        return ''


def total_schools(year):
    if year == 0:
        return '16,080'
    return '16,033'


class Rank(Year):
    def signal(self):
        return -1

    def value(self, soup):
        tag = soup.find_all(class_='infobox_exam_ranking')
        if not tag or self.year_ >= len(tag):
            return ''
        return re.sub(',', '', re.sub(r'Ranked ([0-9,]+) of ' + total_schools(self.year_) + ' schools \(.*', r'\1', tag[self.year_].text))


class Reviews:
    def __init__(self, weight, signal, question, answer):
        self.weight_ = weight
        self.signal_ = signal
        self.question_ = question
        self.answer_ = answer

    def name(self):
        return str(self.question_) + ' ' + str(self.answer_) + ' ' + self.__class__.__name__

    def weight(self):
        return self.weight_

    def signal(self):
        return self.signal_

    def value(self, soup):
        tag = soup.find_all(class_='answers-graph')
        if not tag:
            return ''
        return urllib.parse.parse_qs(urllib.parse.urlparse(tag[self.question_].img['src']).query)['chd'][0][2:].split(',')[self.answer_]


class Oversubscribed(Year):
    def weight(self):
        return 0

    def signal(self):
        return 1

    def value(self, soup):
        tag = soup.find_all(class_=re.compile('infobox_admissions_(not_)?oversubscribed$'))
        if not tag:
            return ''
        oversubscribed = tag[self.year_].text
        if oversubscribed == 'Not Oversubscribed':
            return 0
        if oversubscribed == '∞% Oversubscribed':
            return 'Inf'
        return re.sub(r'([0-9]+%).*', r'\1', oversubscribed)


class Distribution(Year):
    def __init__(self, year, num_years, group):
        super().__init__(year, num_years)
        self.group_ = group
        self.class_ = 'infobox_catchment_chart'

    def name(self):
        return str(self.year_) + ' ' + str(self.group_) + ' ' + self.__class__.__name__

    def weight(self):
        return 0

    def signal(self):
        return 1

    def value(self, soup):
        tag = soup.find(class_=self.class_)
        if not tag:
            return ''
        years = json.loads(tag['data-chart'])
        if self.year_ + 1 >= len(years) :
            return ''
        distance = years[self.year_ + 1][self.group_ + 1]
        if distance == 0:
            return ''
        return distance


class LastDistanceOffered(Distribution):
    def __init__(self, year, num_years):
        super().__init__(year, num_years, 0)
        self.class_ = 'infobox_catchment_ldo_chart'

    def name(self):
        return str(self.year_) + self.__class__.__name__


def get_fields():
        fields = [
            Name(),
            Address(),
            AtCapacity(),
            TextField('Pupils per Teacher', -1),
            TextField('Receives Free School Meals', -1),
            TextField('First Language is not English', -1),
            TextField('Persistent Absence', -1),
            TextField('Pupils with SEN Support', -1),
            OfstedYear(),
            OfstedRating(),
        ]
        for year in range(3):
            fields.extend([
                Rank(year, 3),
                TextFieldYear('Pupils meeting the expected standard', 1, year, 3),
                TextFieldYear('Pupils achieving at a higher standard', 1, year, 3),
                TextFieldYearMultiplier('Reading', 1, year, 3, 2, 0),
                TextFieldYearMultiplier('Maths', 1, year, 3, 2, 0),
                TextFieldYearMultiplier('Reading', 1, year, 3, 2, 1),
                TextFieldYear('Writing', 1, year, 3),
                TextFieldYearMultiplier('Maths', 1, year, 3, 2, 1),
            ])
        for question in range(11):
            fields.extend([
                Reviews(1, 1, question, 0),
                Reviews(0.5, 1, question, 1),
                Reviews(0.5, -1, question, 2),
                Reviews(1, -1, question, 3),
            ])
        fields.append(Reviews(1, 1, 11, 0))
        fields.append(Reviews(1, -1, 11, 1))
        for year in range(5):
            fields.append(Oversubscribed(year, 5))
        for year in range(1, 3):
            fields.append(LastDistanceOffered(year, 3))
        for year in range(7):
            for group in range(3):
                fields.append(Distribution(year, 7, group))
        return fields


def main():
    fields = get_fields()
    for field in fields:
        print(field.weight(), end='\t')
    print()
    for field in fields:
        print(field.signal(), end='\t')
    print()
    for field in fields:
        print(field.name(), end='\t')
    print()
    for file in os.listdir('responses'):
        with open('responses/' + file) as response:
            javascript = json.load(response)['d']
            html = eval(re.sub(r'popUpInfoWindow\((".*?[^\\]").*', r'\1', javascript))
            soup = BeautifulSoup(html, 'html.parser')

            for field in fields:
                print(field.value(soup), end='\t')
            print()


if __name__ == '__main__':
    main()
