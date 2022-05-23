# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 16:28:19 2022

@author: Owner
"""

import requests as req
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import statsmodels.api as sm

path_in = 'C:/Users/Owner/Downloads/'
path_out = 'C:/Users/Owner/Documents/BI/'
file_out1 = 'merged_data.csv'

#Scraping death rate
urltoget='http://www.laalmanac.com/vitals/'
web_path2 ='vi11.php'

r=req.get(urltoget + web_path2)
 
soup = BeautifulSoup(r.content, "html.parser")
rows = soup.find_all('tr')
row_list = list()
    
for tr in rows:
    td = tr.find_all('td')
    row = [i.text for i in td]
    row_list.append(row)

df_death = pd.DataFrame(row_list,columns=['year','death_rate','drop1','drop2','drop3','drop4','drop5'])
df_death = df_death.drop(['drop1', 'drop2', 'drop3', 'drop4', 'drop5'], axis = 1)
df_death = df_death.drop(df_death.index[45:93])
df_death = df_death.dropna()
df_death['year'] = df_death['year'].astype(int)
df_death['death_rate'] = df_death['death_rate'].str.replace(',', '')
df_death['death_rate'] = df_death['death_rate'].str.replace('†', '')
df_death['death_rate'] = df_death['death_rate'].astype(int)

#Scraping birth rate data
web_path1 ='vi06.php#:~:text=Live%20Births%20and%20Birth%20Rates%20Los%20Angeles%20County,%20%2012.0%20%2031%20more%20rows%20'

r=req.get(urltoget + web_path1)
 
soup = BeautifulSoup(r.content, "html.parser")
rows = soup.find_all('tr')
row_list = list()
    
for tr in rows:
    td = tr.find_all('td')
    row = [i.text for i in td]
    row_list.append(row)

df_birth = pd.DataFrame(row_list,columns=['year','birth_rate','drop1','drop2','drop3','drop4'])
df_birth = df_birth.drop(['drop1', 'drop2', 'drop3', 'drop4'], axis = 1)
df_birth = df_birth.dropna()
df_birth['year'] = df_birth['year'].astype(int)
df_birth['birth_rate'] = df_birth['birth_rate'].str.replace(',','')
df_birth['birth_rate'] = df_birth['birth_rate'].astype(int)

#Creating population dataframe by merging
unemployment=pd.read_csv(path_in + 'unemployment.csv')  
unemployment['year'] = unemployment['DATE'].str[-4:]
unemployment = unemployment.drop(['DATE'], axis = 1)
unemployment.drop_duplicates(subset='year', inplace=True)
unemployment = unemployment.drop([372])
unemployment = unemployment.drop([384])
unemployment.rename(columns={'CALOSA7URN' : 'unemployment_rate'}, inplace=True) 
unemployment['year'] = unemployment['year'].astype(int) 

hpi=pd.read_csv(path_in + 'hpi.csv')
hpi['year'] = hpi['DATE'].str[0] + hpi['DATE'].str[1] + hpi['DATE'].str[2] + hpi['DATE'].str[3] 
hpi = hpi.drop(['DATE'], axis = 1)
hpi = hpi.drop(hpi.index[0:15])
hpi = hpi.drop([46])
hpi.rename(columns={'ATNHPIUS06037A' : 'home_price_index'}, inplace=True) 
hpi['year'] = hpi['year'].astype(int) 

inflation=pd.read_csv(path_in + 'inflation.csv')  
inflation['year'] = inflation['DATE'].str[0] + inflation['DATE'].str[1] + inflation['DATE'].str[2] + inflation['DATE'].str[3] 
inflation = inflation.drop(['DATE'], axis = 1)
inflation.drop_duplicates(subset='year', inplace=True)
inflation = inflation.drop(inflation.index[0:10])
inflation.rename(columns={'CUURA421SA0' : 'inflation'}, inplace=True) 
r2018 = {'inflation': 259.22, 'year': '2018'}
r2019 = {'inflation': 267.63, 'year': '2019'}
r2020 = {'inflation': 275.55, 'year': '2020'}
inflation = inflation.append(r2018, ignore_index = True)
inflation = inflation.append(r2019, ignore_index = True)
inflation = inflation.append(r2020, ignore_index = True)
inflation['year'] = inflation['year'].astype(int) 

income=pd.read_csv(path_in + 'income.csv')  
income['year'] = income['DATE'].str[-4:]
income = income.drop(['DATE'], axis = 1)
income.drop_duplicates(subset='year', inplace=True)
income = income.drop([0])
income.rename(columns={'MHICA06037A052NCEN' : 'household_income'}, inplace=True) 
income['year'] = income['year'].astype(int) 

pop=pd.read_csv(path_in + 'pop.csv')  
pop['year'] = pop['DATE'].str[-4:]
pop = pop.drop(['DATE'], axis = 1)
pop = pop.drop(pop.index[0:20])
pop = pop.drop([51])
pop.rename(columns={'CALOSA7POP' : 'population_in_thousands'}, inplace=True) 
pop['year'] = pop['year'].astype(int) 

population_data5 = pd.merge(df_birth, df_death, on ='year', how ="inner")
population_data4 = population_data5.merge(hpi, on ='year', how ="inner")
population_data3 = population_data4.merge(inflation, on ='year', how ="inner")
population_data2 = population_data3.merge(unemployment, on ='year', how ="inner")
population_data1 = population_data2.merge(income, on ='year', how ="inner")
population_data = population_data1.merge(pop, on ='year', how ="inner")

population_data.to_csv(path_out + 'population_data.csv', index = False)


#Creating New variables
LA_pop = population_data.copy()
pop = LA_pop.sort_values('year')

pop['inflation_rate'] = pop['inflation'].pct_change()
pop['inflation_rate'] = pop['inflation_rate'] * 100

pop['home_price_change'] = pop['home_price_index'].pct_change()
pop['home_price_change'] = pop['home_price_change'] * 100

pop['pop'] = pop['population_in_thousands'] * 1000

pop['birth_rate_thousand'] = (pop['birth_rate'] / pop['pop']) * 1000
pop['death_rate_thousand'] = (pop['death_rate'] / pop['pop']) * 1000


pop.dropna(inplace = True)
pop = pop.drop(columns = 'pop')

#Adding Electricity usage df to main
electricity=pd.read_csv(path_in + 'ElectricityByCounty.csv')

electricity_data = electricity.drop(index=[0,1])
df = electricity_data.melt(value_vars=electricity_data.columns[2:len(electricity_data.columns)])
df.rename(columns={'variable' : 'year', 'value' : 'usage'}, inplace= True)
df_electricity = df.drop(index=[31])
df_electricity['year'] = df_electricity['year'].astype(int)

df_merge = pop.merge(df_electricity, how = 'left', left_on= 'year', right_on = 'year')

# Adding cost per kwh
cost = pd.read_csv(path_in + 'APUS49A72610.csv')
cost['DATE'] = pd.to_datetime(cost['DATE'])
cost['year'] = cost['DATE'].dt.year
cost = cost.rename(columns = {'APUS49A72610': 'price_per_kwh'})
cost = cost.drop(index=[82])
cost['price_per_kwh']= pd.to_numeric(cost['price_per_kwh'])
avg_cost = cost[['year', 'price_per_kwh']].groupby('year').mean()

df_merge = df_merge.merge(avg_cost, how = 'left', left_on= 'year', right_on = 'year')

a=df_merge.corr()
#Regression
Y = df_merge.usage
X = df_merge[['population_in_thousands', 'birth_rate_thousand', 'death_rate_thousand']]

model=sm.OLS(Y,X)
result_avg=model.fit()
result_avg.summary()

Y1 = df_merge.price_per_kwh
X1 = df_merge[['inflation']]

model1=sm.OLS(Y1,X1)
result1_avg=model1.fit()
result1_avg.summary()

df_merge.to_csv(path_out + file_out1, sep = ',', index = False)






