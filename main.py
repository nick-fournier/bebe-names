import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import wget
import sys
import os
from datetime import datetime
from zipfile import ZipFile

def bar_progress(current, total, width=80):
  progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
  # Don't use print() as it will print in new line every time.
  sys.stdout.write("\r" + progress_message)
  sys.stdout.flush()

class BebeNames:
    def __init__(self):
        self.url = "https://www.ssa.gov/oact/babynames/names.zip"
        self.databasedir = './data/'
        self.nameszip = 'names.zip'

        self.download()
        self.popularity()

    def download(self, file = "names.zip"):
        zipdir = self.databasedir + self.nameszip
        datadir = self.databasedir + 'names/'

        if not os.path.isdir(self.databasedir):
            os.mkdir(self.databasedir)

        fdate = datetime.fromtimestamp(os.path.getmtime(zipdir)).date()
        if fdate != datetime.today().date():
            os.remove('./data/names.zip')
            wget.download(self.url, "./data/names.zip", bar=bar_progress)

        # Open the newly-created file with ZipFile()
        zf = ZipFile(self.databasedir + self.nameszip)
        # Extract its contents into <extraction_path>
        # note that extractall will automatically create the path
        zf.extractall(path=datadir)
        # close the ZipFile instance
        zf.close()

        # read data
        flist = [x for x in os.listdir(datadir) if ('yob' in x) & ('.txt' in x)]

        names = pd.DataFrame()
        for f in flist:
            tmpdat = pd.read_csv(datadir + f, header=None).rename(columns={0: 'name', 1: 'sex', 2: 'count'})
            tmpdat['year'] = int(f.replace('yob', '').replace('.txt', ''))
            names = names.append(tmpdat)

        self.names = names

    def popularity(self, sex = 'M', scale='minmax'):
        # Filter by sex
        namesdf = self.names[self.names.sex == sex].copy()

        # Bin year into decade
        #namesdf['decade'] = namesdf['year'].apply(lambda x: str(10*round(x/10)) + '-' + str(10*round(x/10) + 9))
        #namesdf = namesdf.groupby(['name', 'sex', 'decade'])['count'].sum('count').reset_index()

        def minmax(x):
            return 100*(x - x.min()) / (x.max() - x.min())

        def zscore(x):
            return (x - x.mean()) / x.std()

        # Normalize by decade
        if scale == 'minmax':
            namesdf['normal'] = namesdf.groupby('year')['count'].transform(lambda x: minmax(x))
        elif scale == 'zscore':
            namesdf['normal'] = namesdf.groupby('year')['count'].transform(lambda x: zscore(x))
        else:
            raise ValueError('Invalid scaling type, must be "minmax" or "zscore".')

        namesdf = namesdf.reset_index(drop=True)

        self.names = namesdf

    def get_quartiles(self):
        namesum = self.names[['name', 'count', 'normal']].groupby('name').sum('normal').reset_index()

        # Appear more than 1000 times
        sns.histplot(data=namesum[namesum['count']>1000], x="normal", bins=100)

        namesum[namesum['count'] > 1000].sort_values('normal', ascending=False).head(10)
        # namesum['normal'].quantile([0, 0.25, 0.5, 0.75, 0.90])
        namesum[namesum['normal'] >= namesum['normal'].quantile(0.90)]


    def get_notrecent(self, last_n_years = 40, percentile = 0.90):

        since_year = datetime.today().year - last_n_years
        namesdf = self.names
        perc_name = str(round(100 * percentile)) + 'th'

        #Get nth percentile
        namesdf[perc_name] = namesdf.groupby('year')['normal'].transform(lambda x: x.quantile(percentile))
        namesdf = namesdf[namesdf['normal'] >= namesdf[perc_name]]

        # Get most popular names in last X years
        recent_names = namesdf[(namesdf.year > since_year) & (namesdf.year < datetime.today().year)].name.unique()

        # Remove recent popular names from previously popular names
        namesdf = namesdf[~namesdf['name'].isin(recent_names)]
        namesdf = namesdf.reset_index(drop=True)

        sns.set_palette(sns.color_palette("Paired"))
        fig, ax = plt.subplots(figsize=[15, 5])
        sns.pointplot(data=namesdf.groupby('year').head(10), x='year', y='normal', hue='name', scale=0.25)
        new_ticks = [i.get_text() for i in ax.get_xticklabels()]
        plt.xticks(range(0, len(new_ticks), 10), new_ticks[::10], rotation=30)
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])  # resize position
        ax.legend(loc='center right', bbox_to_anchor=(1.55, 0.5), ncol=3, markerscale=6, fontsize=8)

        # Get most popular year for each name
        namesdf = namesdf.loc[namesdf.groupby("name")['normal'].idxmax().values]
        namesdf.to_excel(r'.\names.xlsx', sheet_name='most popular by year', index = False)





    def misc(self):
        # topnames = namesdf.sort_values('count', ascending=False).groupby('year')[['name','year','count','normal']].head(10)
        # topnames = topnames.sort_values('year')

        # g = sb.pointplot(data=topnames, x="year", y="normal", hue='name', scale=0.25, aspect=2)
        # sns.set_palette(sb.color_palette("Paired"))
        # box = g.get_position()
        # g.set_position([box.x0, box.y0, box.width * 0.85, box.height])  # resize position
        # new_ticks = [i.get_text() for i in g.get_xticklabels()]
        # plt.xticks(range(0, len(new_ticks), 10), new_ticks[::10], rotation=30)
        # #plt.xticks(rotation=30)
        # g.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1, markerscale=6, fontsize=8)
        # g

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    self = BebeNames()


