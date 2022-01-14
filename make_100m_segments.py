## Shahin's code

# %% Load Data File and call functions

import pandas as pd
import numpy as np
import os, glob
import datetime as dt

# %% Load Unsealed CorpEx Network

corpex_path = r"Q:\MI006 - 21.BI.22 Pavement Analytics App - data refresh - stage 1\1. Data\CorpEx"
corpex_file = "CorpEx_2021_AADT_Sealed.csv"
MMIS_Path =  r"Q:\MI006 - 21.BI.22 Pavement Analytics App - data refresh - stage 1\1. Data\MMIS"

# %% Compact the Nework

# corpex_2021 = pd.read_csv(os.path.join(corpex_path, corpex_file))  ## load 'Unsealed CorpEx network of 2021'  
# corpex_2021 = corpex_2021.loc[:,['ROAD_NO', 'CWAY', 'START_SLK', 'END_SLK', 'START_TRUE', 'END_TRUE', 'RA']]

# network_2021 = stretch(corpex_2021, starts = ['START_SLK', 'START_TRUE'], ends = ['END_SLK', 'END_TRUE']) ## streched the Network SLK into 10m scale
# network_2021 = network_2021.loc[:,['ROAD_NO', 'CWAY', 'START_TRUE', 'END_TRUE', 'RA', 'start', 'end', 'true_start', 'true_end']]

# network_2021_compact = compact(data = network_2021, true_SLK = 'true_start', SLK = 'start', idvars = ['ROAD_NO', 'CWAY'], grouping = ['RA'])

# %% Load compacted Network

compact_net_file = "CorpEx_2021_AADT_Compact_Sealed.csv"

compact_net_2021 = pd.read_csv(os.path.join(MMIS_Path, compact_net_file))  ## load 'Unsealed CorpEx network of 2021' 
compact_net_2021 = compact_net_2021.rename(columns = {'Road': 'ROAD_NO', 'Cway': 'CWAY', 'SLK_From': 'startstart', 'SLK_To': 'startend', 'True_From': 'true_startstart', 'True_To': 'true_startend'})

# %% Create 100m segments from True_Slk

network_2021_100m = make_segments(data = compact_net_2021, SLK_type = 'true', start = 'startstart', end = 'startend', true_start = 'true_startstart', true_end = 'true_startend', segment_size = 100)
network_2021_100m = network_2021_100m.sort_values(by=['ROAD_NO','CWAY','true_startstart'])
network_2021_100m['length'] = round(network_2021_100m['true_startend'] - network_2021_100m['true_startstart'],2)


# network_2021_compact.to_csv(os.path.join(corpex_path, ("CorpEx Network 2021_compact.csv")),index=False)

# %% Adjust the 100m segments with updated SLK

import itertools

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

new_data = network_2021_100m

start_loc = []
end_loc = []
start = None;
for ((index, row),(_,next_row)) in pairwise(new_data.iterrows()):
    #if start is None:
        #start = index;
    
    if ((round(next_row['length'],2) < 0.09) & (row['ROAD_NO'] == next_row['ROAD_NO']) & (row['CWAY'] == next_row['CWAY']) & ((round(next_row['true_startstart']-row['true_startstart'],2)) == 0.1)):
        
        start_loc.append(index)
        end_loc.append(index+1)        
    else:
        pass         

for ((index, row),(_,next_row)) in pairwise(new_data.iterrows()):
    
    if (index+1) in end_loc:
        val_true_slk = np.round((next_row['true_startend'] - row['true_startstart'])/2,2)   # for TRUE_SLK
        new_data['true_startend'].loc[index] = round(row['true_startstart'] + val_true_slk,2)
        new_data['true_startstart'].loc[index+1] = round(row['true_startstart'] + val_true_slk,2)
        
        #val_slk = np.round((next_row['startend'] - row['startstart'])/2,2)                  # for SLK
        new_data['startend'].loc[index] = round(row['startstart'] + val_true_slk,2)
        new_data['startstart'].loc[index+1] = round(row['startstart'] + val_true_slk,2)

new_data['true_length'] = round(new_data['true_startend'] - new_data['true_startstart'],2)
new_data['slk_length'] = round(new_data['startend'] - new_data['startstart'],2)
new_data['Flag'] = np.where((new_data['true_length'] == new_data['slk_length']), 'N', 'Y')
        
network_2021_100m_adjusted = new_data
del new_data

network_2021_100m_adjusted = network_2021_100m_adjusted.rename(columns={ "startstart":"START_SLK", "startend":"END_SLK", "true_startstart": "TRUE_START", "true_startend":"TRUE_END"})
network_2021_100m_adjusted = network_2021_100m_adjusted.reset_index(drop = True)   
#network_2021_100m_adjusted.to_csv(os.path.join(MMIS_Path, ("network_2021_100m_length_adjusted.csv")),index=False)

# %% Functions to manipulate SLK parameters

##Deal with an SLK column as metres in integers to avoid the issue of calculating on floating numbers
def asmetres(var):

    m = round(var*1000).astype(int)

    return m

def gcd_list(items):
    items = list(items)

    def gcd(a, b):
        while b > 0:
            a, b = b, a%b
        return a

    result = items[0]

    for i in items[1:]:
        result = gcd(result, i)
    
    return result

# %%

##Turn each observation into sections of specified lengths

def stretch(data, starts, ends, prefixes = ['', 'true_'], segment_size = 'GCD', keep_ranges = False, sort = None):

    import numpy as np
 

    SLKs = [SLK for SLK in starts + ends]
    new_data = data.copy().reset_index(drop = True) #Copy of the dataset
    new_data = new_data.dropna(thresh = 2)  #drop any row that contain at least two non-missing values.
    
    if type(sort) == list:
        new_data.sort_values(sort, inplace = True)

    #Change SLK variables to 32 bit integers of metres to avoid the issue with calculations on floating numbers
    new_data[SLKs] = new_data[SLKs].apply(asmetres)
    
    if segment_size == 'GCD':
        lengths = new_data[ends[0]] - new_data[starts[0]]
        segment_size = gcd_list(lengths)
        #print(segment_size)
        
    #Reshape the data into size specified in 'obs_length'
    new_data = new_data.reindex(new_data.index.repeat(np.ceil((new_data[ends[0]] - new_data[starts[0]])/segment_size))) #reindex by the number of intervals of specified length between the start and the end.
    for start, prefix in zip(starts, prefixes):
        new_data[prefix + 'start'] = (new_data[start] +  new_data.groupby(level = 0).cumcount()*segment_size)
        print(new_data[start], new_data.groupby(level = 0).cumcount()*segment_size)
        
    for start, end, prefix in zip(starts, ends, prefixes):
    #End SLKs are equal to the lead Start SLKS except where the segment ends
        new_data[prefix + 'end'] = np.where((new_data[prefix + 'start'].shift(-1) - new_data[prefix + 'start']) == segment_size, new_data[prefix+'start'].shift(-1), new_data[end])
        print(prefix + 'end')
        new_data[prefix + 'end'] = new_data[prefix + 'end']/1000
        new_data[prefix + 'start'] = new_data[prefix + 'start']/1000
        
        
    
    new_data = new_data.reset_index(drop = True)
    print(new_data.columns)
    #Drop the variables no longer required
    if not keep_ranges:
        #new_data.drop([SLK for SLK in SLKs], axis = 1, inplace = True)
        new_data = new_data.reset_index(drop = True)
    else: 
        for SLK in SLKs:
            
            new_data[SLK] = new_data[SLK]/1000
           

    return new_data

# %% 
def compact(data, true_SLK = None, lanes = [], SLK = None, obs_length = 10, idvars = [], grouping = [], new_start_col = "start", new_end_col = "end"):
    
    SLKs = [SLK for SLK in [true_SLK, SLK] if SLK is not None]
    
    import numpy as np
    #Sort by all columns in grouping, then by true SLK, then by SLK
    new_data = data.copy().sort_values(idvars + SLKs + lanes).reset_index(drop = True)


    #Change SLK variables to 32 bit integers of metres to avoid the issue with calculations on floating numbers
    for SLK in SLKs:
        new_data[SLK] = asmetres(new_data[SLK])
    
     #Create a column that is a concatenation of all the columns in the grouping
    new_data.insert(0, "groupkey", "")
    for var in grouping+idvars:
        new_data["groupkey"] += new_data[var].astype(str) + '-'
        
    #Create lag and lead columns for SLK, true SLK, and the grouping key to check whether a new group has started
    for var in SLKs:
        new_data['lead_' + var] = new_data[var].shift(-1, fill_value = 1000)
        new_data['lag_' + var] = new_data[var].shift(1, fill_value = 1000)
        
    if None not in [SLK, true_SLK]:
         new_data['diff'] = new_data.loc[:,true_SLK] - new_data.loc[:,SLK]
         new_data['lead_diff'] = new_data['diff'].shift(-1, fill_value = 1000)
         new_data['lag_diff'] = new_data['diff'].shift(1, fill_value = 1000)
         
    new_data['lead_groupkey'] = new_data['groupkey'].shift(-1, fill_value = 'End')
    new_data['lag_groupkey'] = new_data['groupkey'].shift(1, fill_value = 'Start')

        

    #Create columns based on whether they represent the start or end of a section.
    starts, ends = {}, {}
    
    for var in SLKs:
        if None in [SLK, true_SLK]:
            starts[var] = np.where((new_data['lag_' + var] == (new_data[var]-obs_length)) & (new_data['lag_groupkey'] == new_data['groupkey']), False,True) #if the lagged SLKs are not one observation length less than the actual or the lagged group-key is different.
            ends[var] = np.where((new_data['lead_' + var] == (new_data[var] + obs_length)) & (new_data['lead_groupkey'] == new_data['groupkey']), False,True)  #if the lead SLKs are not one observation length more than the actual or the lead group-key is different.
        else:
            starts[var] = np.where((new_data['lag_' + var] == (new_data[var]-obs_length)) & (new_data['lag_groupkey'] == new_data['groupkey'])  & (new_data['lag_diff'] == new_data['diff']), False,True) 
            ends[var] = np.where((new_data['lead_' + var] == (new_data[var] + obs_length)) & (new_data['lead_groupkey'] == new_data['groupkey']) & (new_data['lead_diff'] == new_data['diff']), False,True) 
    
    
    start = np.prod([i for i in starts.values()], axis = 0, dtype = bool)
    end = np.prod([i for i in ends.values()], axis = 0, dtype = bool)

    #Create the compact dataset

    compact_data = new_data.copy()[start][idvars + grouping].reset_index(drop = True) #Data for the id and grouping variables for every start instance.
    new_SLKs = []
    for var in SLKs:
        compact_data.insert(len(idvars),  var + new_start_col, (new_data[start].reset_index(drop = True)[var])/1000)
        compact_data.insert(len(idvars)+1,  var + new_end_col, (new_data[end].reset_index(drop = True)[var] + obs_length)/1000)
        new_SLKs += [var + new_start_col, var + new_end_col]   

    compact_data = compact_data.sort_values(idvars + new_SLKs + lanes).reset_index(drop = True) #Sort data by the location varibles
    
    return compact_data
  
# %%

# Change segment_size = 100 for 100 meter segments
# segment_size = 100
  
def make_segments(data, SLK_type = "both", start = None, end = None, true_start = None, true_end = None, segment_size = 100):
    
    import numpy as np
    
    original = [start, end]
    true = [true_start, true_end]
    starts = [var for var in [start, true_start] if var is not None]
    ends = [var for var in [end, true_end] if var is not None]
    
    new_data = data.copy() #Copy of the dataset
    
    #Describe the SLK_type methods
    if SLK_type not in ['both', 'true', 'original']:
        return print("`SLK_type` must be one of 'both', 'true', or 'original'.")
    
    SLKs = [var for var in original + true if var is not None]
    
    if SLK_type == 'both' and None in SLKs:
        return print("All SLK variables must be declared when using `SLK_type` 'both'.")
    
    if SLK_type == 'original':
        if any(var in true for var in SLKs):
            print("'True' SLK variables will be ignored when using `SLK_type` 'original'.")
            new_data.drop([true_start, true_end], axis = 1, errors = 'ignore')

    if SLK_type == 'true': 
        if any(var in original for var in SLKs):
            print("'Original' SLK variables will be ignored when using `SLK_type` 'true'.")
            new_data.drop([start, end], axis = 1, errors = 'ignore')     
    
    new_data = new_data.dropna(thresh = 2)  #drop any row that contain at least two non-missing values.

    #Change SLK variables to 32 bit integers of metres to avoid the issue with calculations on floating numbers
    for var in SLKs:
        new_data[var] = asmetres(new_data[var])
        print(new_data[var])
    
    #Reshape the data into size specified in 'obs_length'
    print(new_data[0:10])
    print(np.ceil((new_data[ends[0]] - new_data[starts[0]])/segment_size))
    print(starts)
    
    #new_data = new_data.reindex(new_data.index.repeat(np.ceil((new_data[ends[0]] - new_data[starts[0]])/segment_size))) #reindex by the number of intervals of specified length between the start and the end.
    new_data = new_data.reindex(new_data.index.repeat(np.ceil((new_data[ends[1]] - new_data[starts[1]])/segment_size))) #reindex by the number of intervals of specified length between the start and the end.
    for var in starts:
    #Increment the rows by the segment size
        new_data[var] = (new_data[var] + new_data.groupby(level=0).cumcount()*segment_size) 
    print(new_data.groupby(level=0).cumcount())
        
    print(starts)
    for start_,end_ in zip(starts, ends):
    #End SLKs are equal to the lead Start SLKS except where the segment ends
        new_data[end_] = np.where((new_data[start_].shift(-1) - new_data[start_]) == segment_size, new_data[start_].shift(-1), new_data[end_])
    
    new_data[end] = new_data[start] + (new_data[true_end] - new_data[true_start])
    
    #Convert SLK variables back to km
    for var in SLKs:
        new_data[var] = new_data[var]/1000
        
    new_data = new_data.reset_index(drop = True)

    return new_data

