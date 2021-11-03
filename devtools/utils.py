import random, time, os, pandas

def isAllNumbers(x):
    return all([s in ['0','1','2','3','4','5','6','7','8','9'] for s in x])


def isThereNumbers(x):
    return any([s in ['0','1','2','3','4','5','6','7','8','9'] for s in x])


def genUniqueId():
    return "%(rand)s-%(t)s" % {
        "rand": random.SystemRandom().getrandbits(25),
        "t": int(time.time())}


def getLastFile(path, basename=""):
    files = [path+file for file in os.listdir(path) if basename in file]
    return max(files, key=os.path.getctime)


def flushNullCol(df):
    isnull = pandas.isna(df).all()  
    to_remove = isnull[isnull==True].index.tolist()
    if len(to_remove) == 1: to_remove = to_remove[0]
    return df.drop(to_remove, 1)


def UploadTimeSeries(data_path, extension):
    file = pandas.read_csv(data_path + "/" + extension)
    file.index = pandas.to_datetime(pandas.to_numeric(file.Timestamp), unit='s')
    file = file[~file.index.duplicated(keep='last')]
    file = file.sort_index()
    return file[['Open', 'High', 'Low', 'Close', 'Volume']]


def groupedLambda(df, keys, aggregate,):
    grouped = df.groupby(keys).agg(aggregate).reset_index()
    return df.merge(grouped, on=keys, how='left')


def trscomma4pandas(df):
    stringcols = df.applymap(type).eq(str).any()
    for col in stringcols[stringcols].index.tolist():
        df[col] = df[col].str.split(',').str.join('').astype(float)
    return df