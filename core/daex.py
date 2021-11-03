import site, pandas, json, itertools, datetime, numpy, os, traceback, time, pandas
from typing import Union,TypeVar
site.addsitedir("Path/to/Libraries/")
from devtools.net import *
from devtools.utils import *
from devtools.logging import *


class ItalianCentralBank:

    def __init__(self, CHROMEDRIVER_PATH, instructions_path, root= None):
        if not root:
            self.root = os.getcwd().replace("\\","/") + "/icb/"
        else:
            self.root = root

        if not os.path.exists(self.root): os.makedirs(self.root)
        self.driver = WebDriver(CHROMEDRIVER_PATH)
        self.BANKIT_QUERY_ROOT_WB = "https://infostat.bancaditalia.it/inquiry/home?spyglass/taxo:CUBESET=/PUBBL_00/PUBBL_00_06/"

        with open(instructions_path) as f:
            self.instructions = json.load(f)

        # Generate all the working folders
        self.generateFolders()

        # Initialize the logging file.
        self.logger = logging(
            filename= self.root + self.instructions['paths']['icb']['log'],
        )

    
    def generateFolders(self):
        for key in self.instructions["paths"]["icb"].keys():
            if ((not os.path.exists(self.root + self.instructions["paths"]["icb"][key])) & (key != "log")):
                os.makedirs(self.root + self.instructions["paths"]["icb"][key])


    def query(self, endpoint):
        try:
            self.driver.get(self.BANKIT_QUERY_ROOT_WB+f"/PUBBL_00_06_06&ITEMSELEZ={endpoint}:true&OPEN=false/&ep:LC=EN&COMM=BANKITALIA&ENV=LIVE&CTX=DIFF&IDX=2&/view:CUBEIDS=/")
            exportButton = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[3]/section[2]/div[4]/div[2]/button[2]')))
            exportButton.click()
            time.sleep(10)
            getFileButton = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, 'html/body/div[5]/div[6]/div/div/div[3]/button[1]')))
            getFileButton.click()
            time.sleep(10)
            self.logger.write(
                msg=f"[ICB] - [query]: File correcly stored in {getLastFile('C:/Users/pietr/Downloads/')}.",
                level="INFO",
            )
        except Exception as e:
            errorKey = genUniqueId()
            with open(self.root+self.instructions['paths']['icb']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                traceback.print_exc(file=f)
            self.logger.write(
                msg=f"[ICB] - [query]: Traceback stored in /{errorKey}.txt. | Release not found.",
                level="CRITICAL",
            )

    
    def driverClose(self):
        self.driver.close()


class WorldEconomicOutlook:

    def __init__(self, instructions_path, root= None):
        if not root:
            self.root = os.getcwd().replace("\\","/") + "/weo/"
        else:
            self.root = root
        
        if not os.path.exists(self.root): os.makedirs(self.root)
        with open(instructions_path) as f:
            self.instructions = json.load(f)

        # Generate all the working folders
        self.generateFolders()

        # Initialize the logging file.
        self.logger = logging(
            filename= self.root + self.instructions['paths']['weo']['log'],
        )


    def retrieveDates(self,):
        dates = list()
        for year in numpy.arange(2007, datetime.datetime.now().year + 1):
            for release in ['Apr', 'Oct']:
                dates.append(tuple([year, release]))
        return dates


    def generateFolders(self):
        for key in self.instructions["paths"]["weo"].keys():
            if ((not os.path.exists(self.root + self.instructions["paths"]["weo"][key])) & (key != "log")):
                os.makedirs(self.root  + self.instructions["paths"]["weo"][key])


    def checkLatestUpdate(self, verbose=False, months=['Apr', 'Oct']):
        current_year = datetime.datetime.now().year
        available_releases = list()
        possible_releases = list(itertools.product([current_year - 1, current_year], months))
        for possible_release in possible_releases:
            try:
                NET().reqResponse(
                    self.instructions["urls"][
                        "WEO"] + f"/{possible_release[0]}/WEO{possible_release[1]}{possible_release[0]}all")
                NET().reqResponse(
                    self.instructions["urls"][
                        "WEO"] + f"/{possible_release[0]}/WEO{possible_release[1]}{possible_release[0]}alla")
                available_releases.append(possible_release)
            except Exception:
                errorKey = genUniqueId()
                with open(self.root+self.instructions['paths']['weo']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                    traceback.print_exc(file=f)
                self.logger.write(
                    msg=f"[WEO] - [checkLatestUpdate]: {possible_release} | Traceback stored in /{errorKey}.txt. | Release not found.",
                    level="CRITICAL",
                )
        self.logger.write(
            msg=f"[WEO] - [checkLatestUpdate]: Last available release: {available_releases[-1]}.",
            level="INFO",
        )
        if verbose:
            print(f"[WEO] - [checkLatestUpdate]: Last available release: {available_releases[-1]}.")
        self.latest_available_release = available_releases[-1]


    def LoadVersion(self,):
        with open(self.root + self.instructions["paths"]["weo"]["releases"] + f"/{self.latest_available_release[0]}-{self.latest_available_release[1]}-byCountries.xls",
                  'wb') as f:
            f.write(NET().reqResponse(
                self.instructions["urls"]["WEO"] + f"/{self.latest_available_release[0]}/WEO{self.latest_available_release[1]}{self.latest_available_release[0]}all.ashx").content)
        with open(self.root + self.instructions["paths"]["weo"]["releases"] + f"/{self.latest_available_release[0]}-{self.latest_available_release[1]}-byCountryGroups.xls",
                  'wb') as f:
            f.write(NET().reqResponse(
                self.instructions["urls"]["WEO"] + f"/{self.latest_available_release[0]}/WEO{self.latest_available_release[1]}{self.latest_available_release[0]}alla.ashx").content)
        self.UpdateDataHub(self.latest_available_release)


    def ashx2pandas(self, filename):
        try:
            df = pandas.read_csv(filename, delimiter="\t", encoding="iso-8859-1")
            if df.isnull().iloc[0, 0]:
                raise ValueError("Error in Encoding format.")
        except Exception:
            try:
                df = pandas.read_csv(filename, delimiter="\t", encoding="UTF-16 LE")
                # df.dropna(how="all", axis=1, inplace=True)
            except Exception:
                errorKey = genUniqueId()
                with open(self.root + self.instructions['paths']['weo']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                    traceback.print_exc(file=f)
                self.logger.write(
                    msg=f"[WEO] - [ashx2pandas]: Traceback stored in /{errorKey}.txt. | There was an error trying to load the .xls file.",
                    level="CRITICAL",
                )
        return df.loc[df.Units.notna()]


    def UpdateDataHub(self, release, clusters=['byCountries', 'byCountryGroups']):
        def WEO_Iso_Code(x):
            if x == 'byCountryGroups':
                return "WEO Country Group Code"
            elif x == 'byCountries':
                return "WEO Country Code"
            else:
                return None

        def WEO_Country_Label(x):
            if x == 'byCountryGroups':
                return "Country Group Name"
            elif x == 'byCountries':
                return "Country"
            else:
                return None

        dataDict = dict()
        metadataDict = dict()
        for cluster in clusters:
            try:
                dh = self.ashx2pandas(
                    self.root + f"/files/datahub/versions/{release[0]}-{release[1]}-{cluster}.xls")
                dh["Records"] = dh[[x for x in dh.columns if isAllNumbers(x)]].values.tolist()
                dh["Dates"] = [[x for x in dh.columns if isAllNumbers(x)] for _ in range(dh.shape[0])]
                dh.index = dh['WEO Subject Code']
                for zone in dh[WEO_Country_Label(cluster)].unique():
                    # Fill meta-Data dict
                    metadataDict[zone] = dict()
                    metadataDict[zone][WEO_Iso_Code(cluster)] = \
                    dh.loc[(dh[WEO_Country_Label(cluster)] == zone)][WEO_Iso_Code(cluster)].iloc[0]
                    if cluster == 'byCountries':
                        metadataDict[zone]['ISO'] = dh.loc[(dh[WEO_Country_Label(cluster)] == zone)]['ISO'].iloc[0]
                    # Fill data-Dict
                    dataDict[zone] = dict()
                    dataDict[zone] = dh.loc[(dh[WEO_Country_Label(cluster)] == zone)][[
                        'Subject Descriptor', 'Subject Notes', 'Units', 'Scale', 'Country/Series-specific Notes',
                        'Records', 'Dates']].to_dict(orient='index')
            except Exception:
                errorKey = genUniqueId()
                with open(self.root + self.instructions['paths']['weo']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                    traceback.print_exc(file=f)
                self.logger.write(
                    msg=f"[WEO] - [UpdateDataHub]: {cluster} - {release} | Traceback stored in /{errorKey}.txt. | There was an error trying to fetch the data into JSON Format.",
                    level="CRITICAL",
                )
        with open(self.root + self.instructions['paths']['weo']['datahub'] + f"/{release[0]}-{release[1]}-WEO-database.json",
                  "w+") as f:
            json.dump(dataDict, f, indent=3)
        with open(self.root + self.instructions['paths']['weo']['datahub'] + f"/{release[0]}-{release[1]}-WEO-metadata.json",
                  "w+") as f:
            json.dump(metadataDict, f, indent=3)


    def get(self, areas, variables= None, download= False):
        version = [path for path in os.listdir(self.root + "files/datahub/") if "database" in path][0]
        
        # Load the Outlook.
        with open(self.root + "files/datahub/" + version) as f:
            file = json.load(f)

        series, dates = dict(), list()
        for area in areas:
            try:
                if not variables: variables = file[area].keys()
                for variable in variables:
                    try:
                        series[f"{area}_{variable}"] = file[area][variable]['Records']
                        dates.append(file[area][variable]['Dates'])
                    except Exception as msg:
                        errorKey = genUniqueId()
                        with open(self.root + self.instructions['paths']['weo']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                            traceback.print_exc(file=f)
                        self.logger.write(
                            msg=f"[WEO] - [get]: Traceback stored in /{errorKey}.txt.",
                            level="WARNING",
                        )
        
            except Exception as msg:
                errorKey = genUniqueId()
                with open(self.root + self.instructions['paths']['weo']['deepLog'] + f"/{errorKey}.txt", "w+") as f:
                    traceback.print_exc(file=f)
                self.logger.write(
                    msg=f"[WEO] - [get]: Traceback stored in /{errorKey}.txt.",
                    level="CRITICAL",
                )

        if dates.count(dates[0]) == len(dates):
            df = pandas.DataFrame(series, pandas.to_datetime(dates[0]))
            df = flushNullCol(df)
            if not download:
                return df
            else:
                df.to_excel(download + f"/weo_extraction_{genUniqueId()}.xlsx")
        else:
            raise ValueError("Different dates lenght.")