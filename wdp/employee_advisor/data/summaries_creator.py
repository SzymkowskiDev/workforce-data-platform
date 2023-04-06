import pandas as pd
from wdp.utilities import app_source_path
from IPython.display import display
from numpy import NaN, quantile


pd.set_option("display.max_columns", 23)


data_path = app_source_path() / 'employee_advisor' / 'data'
data = pd.read_csv(data_path / 'job_offers.csv')

currencies = {
    NaN: 1,
    'pln': 1,
    'usd': 4.3,
    'eur': 1.9,
    'gbp': 5.35,
    'chf': 4.74,
}


data['midpoints'] = ((data['salary_from'] + data['salary_to']) // 2) * data['currency'].apply(lambda x: currencies.get(x, 1))
data.dropna(axis='index', subset='midpoints', inplace=True)


def stats_for_group(groupname):
    stats = data.groupby(groupname)['midpoints'].aggregate(
        ['median', 'mean', 'quantile', 'count', 'min', 'max', 'std',
         ('quantile10', lambda series: quantile(series, 0.1)),
         ('quantile20', lambda series: quantile(series, 0.2)),
         ('quantile30', lambda series: quantile(series, 0.3))]
    )

    return stats

def stats_for_skills():
    skills = data.columns[22: -10]
    skills_data = data[list(skills) + ['midpoints']]
 
def summaries():
    stats_for_group('company_name').to_csv(data_path / "company_summary.csv", index=False)
    stats_for_group('marker_icon').to_csv(data_path / "marker_icon_summary", index=False)
    stats_for_group('experience_level').to_csv(data_path / "experience_level_summary.csv", index=False)
    stats_for_group('city').to_csv(data_path / "city_summary.csv", index=False)


if __name__ == '__main__':
    # stats_for_skills()
    summaries()