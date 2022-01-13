import pandas as pd
import seaborn as sb
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

    def popularity(self, sex = 'M'):
        # Filter by sex
        namesdf = self.names[self.names.sex == sex].copy()

        # Bin year into decade
        #namesdf['decade'] = namesdf['year'].apply(lambda x: str(10*round(x/10)) + '-' + str(10*round(x/10) + 9))
        #namesdf = namesdf.groupby(['name', 'sex', 'decade'])['count'].sum('count').reset_index()

        # Normalize by decade
        namesdf['normal'] = namesdf.groupby('year')['count'].transform(lambda x: (x - x.mean()) / x.std())
        namesdf = namesdf.reset_index()


    def misc(self):
        #dates = {'start': datetime.today().year - 30, 'end': datetime.today().year}
        #namesdf = namesdf[(namesdf.year > dates['start']) & (namesdf.year < dates['end'])]


        # topnames = namesdf.sort_values('count', ascending=False).groupby('year')[['name','year','count','normal']].head(10)
        # topnames = topnames.sort_values('year')

        # g = sb.pointplot(data=topnames, x="year", y="normal", hue='name', scale=0.25, aspect=2)
        # sb.set_palette(sb.color_palette("Paired"))
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


