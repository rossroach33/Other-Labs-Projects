# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 12:49:49 2022

@author: Owner
"""

import io
import pandas as pd
import requests as r

path= 'C:/Users/Owner/Documents/BI/'

url = 'http://drd.ba.ttu.edu/isqs3358/hw/hw2/'

file_1 = 'powergeneration.csv'
file_2 = 'models.csv'
file_3 = 'region.csv'

file_out1 = 'region_aggregate.csv'
file_out2 = 'high_efficiency_model.csv'
file_out3 = 'operation_hours_raises.csv'

#Pulling files into DFs

res = r.get(url + file_1)
res.status_code
df_power = pd.read_csv(io.StringIO(res.text)) 

res = r.get(url + file_2)
res.status_code
df_model = pd.read_csv(io.StringIO(res.text)) 

res = r.get(url + file_3)
res.status_code
df_reg = pd.read_csv(io.StringIO(res.text)) 

#Dropping missing data in df_power prior to merging other data sets for best results on merge

df_power.dropna(inplace = True)

print('I dropped all NAs because I dont know how to fill in textual values easily')

#Merging df_model and df_reg to df_power

dffinal = df_power.merge(df_model, how = 'inner', left_on = 'model_cd', right_on = 'modelcd')
dffinal = dffinal.merge(df_reg, how = 'inner', left_on = 'region_cd', right_on = 'regioncd')

#Dropping repeated columns from post merge DF
dffinal = dffinal.drop(columns = ['modelcd','regioncd'])

#Creating Revenue per kilowatt column

dffinal['Revenue_per_kilowatt'] = dffinal['RevenueProduced'] / dffinal['kilowatt_production']

#Creating Net Profit for First Year

dffinal['net_profit_for_first_year_of_installation'] = dffinal['RevenueProduced'] - dffinal['yearlyupkeep']

#Creating Hours per Year

dffinal['HoursPerYearOfOperation'] = dffinal['HoursPerWeekOfOperation'] * 52

#Creating Maintenance cost per year

dffinal['MaintenanceCostPerYear'] = dffinal['yearlyupkeep'] / dffinal['HoursPerYearOfOperation']

#Creating Efficiency Column

dffinal['Efficiency'] = 'low'

for index, row in dffinal.iterrows():
    if row['MaintenanceCostPerYear'] > 1 and row['kilowatt_production'] < 3:
        dffinal.at[index,'Efficiency'] = 'high'
    elif (row['MaintenanceCostPerYear'] > 0.5 and row['MaintenanceCostPerYear'] < 1) and (row['kilowatt_production'] > 3 and row['kilowatt_production'] < 6):
        dffinal.at[index,'Efficiency'] = 'high'
    elif row['MaintenanceCostPerYear'] < 0.5  and (row['kilowatt_production'] > 6 and row['kilowatt_production'] < 9):
        dffinal.at[index,'Efficiency'] = 'high'
    else:
        dffinal.at[index,'Efficiency'] = 'low'
        
#Computing Average by region

df_avg = dffinal[['region_name','Revenue_per_kilowatt', 'HoursPerYearOfOperation', 'MaintenanceCostPerYear']].groupby('region_name').mean()

df_avg.to_csv(path + file_out1, sep = ',', index = True)

#Creating High Efficiency DF

df_high = dffinal[dffinal['Efficiency'] == 'high']

df_high.to_csv(path + file_out2, sep = ',', index = False, columns = ['model_cd', 'modelname', 'installcost', 'yearlyupkeep'])

#Creating hourly increase df

dffinal['updated_hour'] = dffinal['HoursPerWeekOfOperation'] * 1.06
dffinal['updated_hour'][dffinal['State'] == 'OK'] = dffinal['HoursPerWeekOfOperation'] * 1.045
dffinal['updated_hour'][dffinal['State'] == 'NM'] = dffinal['HoursPerWeekOfOperation'] * 1.04

dffinal['hour_diff'] = dffinal['updated_hour'] - dffinal['HoursPerWeekOfOperation'] 

df_high2 = dffinal[dffinal['Efficiency'] == 'high']
df_sum = df_high2[['modelname','HoursPerWeekOfOperation', 'updated_hour', 'hour_diff']].groupby('modelname').sum()

df_sum.to_csv(path + file_out3, sep = ',', index = True)





