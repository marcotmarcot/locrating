#!/usr/bin/python3

import json
import re
from bs4 import BeautifulSoup

class Column:
    def name(self):
        return self.__class__.__name__


class Name(Column):
    def signal(self):
        return ''

    def value(self, soup):
        return soup.find(class_='infobox_name').text


class AtCapacity(Column):
    def signal(self):
        return 1

    def value(self, soup):
        return re.sub(r'At ([0-9]+)% Capacity.*', r'\1%', soup.find(id='capacity').text)

class TextFieldYearMultiplier:
    def __init__(self, name, signal, year, multiplier, offset):
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
        return soup.find_all(text=self.name_)[self.year_ * self.multiplier_ + self.offset_].parent.next_sibling.text


class TextFieldYear(TextFieldYearMultiplier):
    def __init__(self, name, signal, year):
        super().__init__(name, signal, year, 1, 0)

    def name(self):
        return str(self.year_) + ' ' + self.name_


class TextField(TextFieldYear):
    def __init__(self, name, signal):
        super().__init__(name, signal, 0)

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


class Rank:
    def __init__(self, year):
        self.year_ = year

    def name(self):
        return str(self.year_) + ' rank'

    def signal(self):
        return 1

    def value(self, soup):
        return re.sub(r'Ranked ([0-9]+) of 16,080 schools \(.*', r'\1', soup.find_all(class_='infobox_exam_ranking')[self.year_].text)


class Oversubscribed:
    def __init__(self, year):
        self.year_ = year

    def name(self):
        return str(self.year_) + ' Oversubscribed'

    def signal(self):
        return 1

    def value(self, soup):
        oversubscribed = soup.find_all(class_=re.compile('infobox_admissions_(not_)?oversubscribed$'))[self.year_].text
        if oversubscribed == 'Not Oversubscribed':
            return 0
        return re.sub(r'([0-9]+%).*', r'\1', oversubscribed)


def main():
    with open('response') as file:
        javascript = json.load(file)['d']
        html = re.sub(r'popUpInfoWindow\("(.*?[^\\])".*', r'\1', javascript)
        soup = BeautifulSoup(html, 'html.parser')
        fields = [
            Name(),
            AtCapacity(),
            TextField('Pupils per Teacher', 1),
            TextField('Receives Free School Meals', -1),
            TextField('First Language is not English', -1),
            TextField('Persistent Absence', -1),
            TextField('Pupils with SEN Support', -1),
            OfstedYear(),
            OfstedRating(),
            Rank(0),
        ]
        for year in range(3):
            fields.extend([
                TextFieldYear('Pupils meeting the expected standard', 1, year),
                TextFieldYear('Pupils achieving at a higher standard', 1, year),
                TextFieldYearMultiplier('Reading', 1, year, 2, 0),
                TextFieldYearMultiplier('Maths', 1, year, 2, 0),
                TextFieldYearMultiplier('Reading', 1, year, 2, 1),
                TextFieldYear('Writing', 1, year),
                TextFieldYearMultiplier('Maths', 1, year, 2, 1),
            ])
        for year in range(5):
            fields.extend([
                Oversubscribed(year),
            ])
        for field in fields:
            print(field.signal(), end='\t')
        print()
        for field in fields:
            print(field.name(), end='\t')
        print()
        for field in fields:
            print(field.value(soup), end='\t')
        print()


if __name__ == '__main__':
    main()
