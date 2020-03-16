import pandas as pd
from datetime import datetime

"""
Outbreaks in each region / country occurs on a different timeline.
If we want to compare them, we'll have to shift the graphs and establish a Day 0.

Currently 3 different decision functions are supported. Day 0 will be considered the first day when:

- new_case_count: The number of new cases becomes larger than threshold.
- total_case_count: The total number of cases becomes larger than threshold.
- normalized_total_case_count: The total number of cases per million people
"""
def new_case_count(row, total, threshold=5):
    return row['NewConfCases'] >= threshold

def total_case_count(row, total, threshold=100):
    return total >= threshold

def normalized_total_case_count(row, total, threshold=2):
    return (total / row['population']) >= threshold


DECISION_FUNCTIONS = {
    'new_case_count': new_case_count,
    'total_case_count': total_case_count,
    'normalized_total_case_count': normalized_total_case_count
}


def pre_process(data, decision_function, **kwargs):
    data['date'] = data['DateRep'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
    data = data.sort_values(by=['CountryExp', 'date'])
    countries = data['CountryExp'].unique()
    stepData = []

    for country in countries:
        ind = 0
        total = 0
        total_deceased = 0

        for _, row in data[data.CountryExp == country].iterrows():
            total += row['NewConfCases']
            total_deceased += row['NewDeaths']

            if DECISION_FUNCTIONS[decision_function](row, total, **kwargs):

                if total == row['NewConfCases']:
                    increase = 100
                else:
                    increase = (row['NewConfCases'] / (total - row['NewConfCases'])) * 100

                stepData.append({
                    'country': country,
                    'days': ind,
                    'total': total,
                    'total_deceased': total_deceased,
                    'new': row['NewConfCases'],
                    'new_deceased': row['NewDeaths'],
                    'population': row['population'],
                    'increase': increase
                })

                ind += 1

    df = pd.DataFrame(stepData, columns=[
        'country', 'new', 'total', 'days', 'new_deceased', 'total_deceased', 'increase',
        'total_per_mil', 'new_per_mil', 'new_deceased_per_mil', 'total_deceased_per_mil', 'population'
    ])

    for c in ['new', 'total', 'days', 'new_deceased', 'total_deceased']:
        df['{}_per_mil'.format(c)] = df[c] / df['population']

    return df