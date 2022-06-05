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
        return soup.find(text='Address').parent.parent.contents[1].contents[-1]


class AtCapacity(Column):
    def weight(self):
        return 0

    def signal(self):
        return 1

    def value(self, soup):
        return re.sub(r'At ([0-9]+)% Capacity.*', r'\1%', soup.find(id='capacity').text)


class White(Column):
    def weight(self):
        return 1

    def signal(self):
        return -1

    def value(self, soup):
        return float(TextField('White, British', 1).value(soup)[:-1]) + float(TextField('White, Other', 1).value(soup)[:-1])


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
    def __init__(self, signal, phrasings):
        self.signal_ = signal
        self.phrasings_ = phrasings

    def name(self):
        return self.phrasings_[0]

    def weight(self):
        return 1

    def signal(self):
        return self.signal_

    def value(self, soup):
        for phrasing in self.phrasings_:
            text =  soup.find(text=phrasing)
            if text:
                break
        if not text:
            return ''
        img = text.parent.next_sibling.next_sibling
        if not img or img.name != 'img':
            img = text.parent.next_sibling.find('img')
            if not img:
                img = text.parent.parent.find('img')
        answers = urllib.parse.parse_qs(urllib.parse.urlparse(img['src']).query)['chd'][0].split(':')[1].split(',')
        answers = [int(answer) for answer in answers]
        total = sum(answers)
        if total == 0:
            return ''
        if len(answers) == 2:
            if self.signal_ == 1:
                return answers[0]/total
            return answers[1]/total
        if self.signal_ == 1:
            if len(answers) == 6:
                return 3*answers[0]/total + 2*answers[1]/total + answers[3]/total
            return 2*answers[0]/total + answers[1]/total
        if len(answers) == 6:
            return 2*answers[4]/total + answers[3]/total
        return 2*answers[3]/total + answers[2]/total


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
            White(),
            TextField('Pupils per Teacher', -1),
            TextField('Receives Free School Meals', -1),
            TextField('First Language is not English', 1),
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
        questions = [
            ['1. My child is happy at this school'],
            ['2. My child feels safe at this school'],
            [
                '3. My child makes good progress at this school',
                '9. My child does well at this school.',
            ],
            [
                '3. The school makes sure its pupils are well behaved.',
                '7. This school makes sure its pupils are well behaved',
            ],
            ['4. My child is well looked after at this school'],
            [
                '4. My child has been bullied and the school dealt with the bullying quickly and effectively.',
                '8. This school deals effectively with bullying',
            ],
            ['5. My child is taught well at this school'],
            ['5. The school makes me aware of what my child will learn during the year.'],
            ['6. My child receives appropriate homework for their age'],
            [
                '6. When I have raised concerns with the school they have been dealt with properly.',
                '10. This school responds well to any concerns I raise',
            ],
            ['7. My child has SEND, and the school gives them the support they need to succeed.'],
            ['8. The school has high expectations for my child.'],
            ['9. This school is well led and managed'],
            [
                '10. The school lets me know how my child is doing.',
                '11. I receive valuable information from the school about my child’s progress',
            ],
            ['11. There is a good range of subjects available to my child at this school.'],
            [
                '12. Would you recommend this school to another parent?',
                '14. I would recommend this school to another parent.',
            ],
            ['12. My child can take part in clubs and activities at this school.'],
            ['13. The school supports my child’s wider personal development.'],
        ]
        for question in questions:
            for signal in [1, -1]:
                fields.append(Reviews(signal, question))
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
        if field.weight() != 0:
            print(field.weight(), end='\t')
    print()
    for field in fields:
        if field.weight() != 0:
            print(field.signal(), end='\t')
    print()
    for field in fields:
        if field.weight() != 0:
            print(field.name(), end='\t')
    print()
    for file in os.listdir('responses'):
        with open('responses/' + file) as response:
            javascript = json.load(response)['d']
            html = eval(re.sub(r'popUpInfoWindow\((".*?[^\\]").*', r'\1', javascript))
            soup = BeautifulSoup(html, 'html.parser')

            for field in fields:
                if field.weight() != 0:
                    print(field.value(soup), end='\t')
            print()


if __name__ == '__main__':
    main()
