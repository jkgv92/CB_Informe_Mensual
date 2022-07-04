#!/usr/bin/env python
# coding: utf-8

# ## Proyecto monitoreo Bancolombia -- Reporte semanal
# 

# In[1]:




from tkinter import Variable
import requests
import pandas as pd
import json
import time
from datetime import datetime
from matplotlib import pyplot as plt

import os
from dotenv import dotenv_values
config = dotenv_values(".env")

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)


class Ubidots:

    def sendDatatoUbidots(pload, headers, request):
        r = requests.post(request,headers=headers, json=pload)

        if  200 <= r.status_code <= 299:
            print("Sent",r.text,"with response code: ",r.status_code)

        if  400 <= r.status_code <= 499:
            print("Retrying...", r.text)
            time.sleep(5)
                
        time.sleep(1)

        return r.text


    def makeUbidotsPayload(value,timestamp,timestampformat):

        pload = { "value": value,
                "timestamp": str(int(datetime.timestamp(datetime.strptime(timestamp,timestampformat))))+'000'}
        return pload


    def makeUbidotsRequest(device_id,variable_id):

        request = 'https://industrial.api.ubidots.com/api/v1.6/devices/'+device_id+'/'+variable_id+'/values'+'/?force=true'

        return request



    def makeUbidotsHeaders(TOKEN):

        headers = {'X-Auth-Token':TOKEN, 'Content-Type':'application/json'}

        return headers

    def Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, TOKEN):
        try:
            datarange_object =  {'start' : int(datetime.timestamp(datetime.strptime(datarange['start'] + 'T00:00:00',timestamp_format))), 'end' : int(datetime.timestamp(datetime.strptime(datarange['end'] + 'T00:00:00',timestamp_format)))}


            pload = {'token': token}

            r = requests.get('https://industrial.api.ubidots.com/api/v1.6/devices/' + device_label + '/' + variable_label + '/values?page_size=1?&start=' + str(datarange_object['start'])+'000'+'&end='+str(datarange_object['end']) + '000', params = pload)

            df = pd.json_normalize(r.json(), record_path =['results'])

            timestamps = df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            df.set_index('timestamp', inplace=True)
            df["created_at"] = pd.to_datetime(df["created_at"], unit='ms')
            df.drop(['created_at'], axis=1, inplace=True)
            df = df.reindex(index=df.index[::-1])

            
            
        except: 
            pass

        return df.rename(columns={"value": variable_label})

        

    
    def get_device_group_devices(token, device_group_label):
        
        pload = {'token':token}
        r = requests.get('https://industrial.api.ubidots.com/api/v2.0/device_groups/'+device_group_label+'/devices/?token='+token, params=pload)

        r.text
        JSON = r.json()

        devices = {
            "device_name" : [],
            "id" : [],
            "label" : []
            }

        for JSON_item in JSON['results']:
            devices["device_name"].append(JSON_item['name'])
            devices["id"].append(JSON_item['id'])
            devices["label"].append(JSON_item['label'])

        return devices

    
    def get_concatenated_dataframe_multiple_devices(df,device_group_devices, variable_label,datarange, timestamp_format, token):
        for i in range(1,len(device_group_devices["device_name"])):
            device_label = device_group_devices["label"][i]
            req_data =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)        
            df = df.merge(req_data,  how='outer')
        return df

    
    def get_all_variables_from_device(token, device_key):
        
        pload = {'token':token}
        r = requests.get('https://industrial.api.ubidots.com/api/v2.0/devices/'+device_key+'/variables/?token='+token, params=pload)

        r.text
        JSON = r.json()

        variables = {
            "variable_name" : [],
            "variable_id" : [],
            "variable_label" : []
            }

        for JSON_item in JSON['results']:
            variables["variable_name"].append(JSON_item['name'])
            variables["variable_id"].append(JSON_item['id'])
            variables["variable_label"].append(JSON_item['label'])

        return variables


    def get_concatenated_dataframe_from_device(df,variables, device_label,datarange,variables_to_download, timestamp_format, token):
            for i in range(1,len(variables["variable_name"])):

                variable_label = variables["variable_label"][i]

                if variable_label in variables_to_download:
                    req_data =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)        
                    df = df.merge(req_data, left_on='timestamp', right_on='timestamp', how='left')
                    
            return df


# In[2]:


token = config["token"]
device_group_label = '61cb3d7eb154cc2dd4a72192'
datarange = { 'start': '2022-06-19',
            'end': '2022-06-26'}
timestamp_format = "%Y-%m-%dT%H:%M:%S"

devices = Ubidots.get_device_group_devices(token, device_group_label)


# ## Sedes disponibles

# In[3]:



print("El rango de visualización de este informe es desde: ", datarange['start'], " hasta: ", datarange['end'])
print("")
devices["device_name"]


# ## BC 291 - Las Palmas

# In[4]:




device_label = devices["label"][0]
device_name = devices["device_name"][0]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Manejo adecuado de las luces durante fin de semana
# * Consumo constante de energía en circuito de Aires durante fin de semana ~ 12 kWh con pico durante una hora aproximadamente el lunes 20 de junio
# * Se visualizan consumos anómalos de energía asociados a pérdida de datos en el sistema de monitoreo

# ## BC 90 - Megamall

# In[5]:




device_label = devices["label"][1]
device_name = devices["device_name"][1]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Manejo adecuado de las luces durante fin de semana
# * Consumo nocturno asociado casi en su totalidad al circuito de iluminación
# * Consumo en circuito de Aire acondicionado durante el Domingo 26 de junio ~ 40 kWh 

# ## BC 799 - Floridablanca

# In[6]:



device_label = devices["label"][2]
device_name = devices["device_name"][2]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# In[ ]:





# ### **Hallazgos**:
# 
# * Consumo nocturo del circuito de Aire acondicionado durante el Lunes festivo, 20 de Junio ~ 20 kWh
# * Consumo atípico del circuito de aire acondicionado, se continuará monitoreando

# ## BC 749 - Santa Monica

# In[7]:




device_label = devices["label"][3]
device_name = devices["device_name"][3]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia, consumo adecuado en el circuito de Aire acondicionado e Iluminación con consumos residuales ~ 2 kWh posiblemente causados por la presencia de algún cajero o sistemas de seguridad

# ## BC 66 - Palmira

# In[8]:



device_label = devices["label"][4]
device_name = devices["device_name"][4]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo de Aire acondicionado durante fines de semana ~ 12 kWh durante todo el día del Domingo 19 y Lunes 20 de junio
# 

# ## BC 205 - Villa Colombia

# In[9]:



device_label = devices["label"][5]
device_name = devices["device_name"][5]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo de Aire acondicionado durante periodos nocturnos y fines de semana ~ 4 kWh
# * Se presenta una pérdida de datos durante la madrugada del Miércoles 22 de Junio, se seguirá monitoreando

# ## BC 424 - Honda

# In[10]:




device_label = devices["label"][6]
device_name = devices["device_name"][6]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia

# ## BC 863 - Los Patios

# In[11]:




device_label = devices["label"][7]
device_name = devices["device_name"][7]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo residual en circuito de aire acondicionado ~ 4 kWh durante las noches

# ## BC 834 - San Mateo

# In[12]:




device_label = devices["label"][8]
device_name = devices["device_name"][8]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Baja significativa de consumo durante el niércoles 22 de junio, posible pérdida de datos, se seguirá monitoreando

# ## BC 044 - Piedecuesta

# In[13]:



device_label = devices["label"][9]
device_name = devices["device_name"][9]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Poca contribución al consumo por parte del circuito de HVAC, menor al 15% del consumo total, se sugiere continuar monitoreando la situación

# ## BC 776 - Lebrija

# In[14]:



device_label = devices["label"][10]
device_name = devices["device_name"][10]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumos residuales en el circuito de Aire acondicionado ~ 4 kWh durante las noches

# ## BC 792 - Paseo del comercio

# In[15]:



device_label = devices["label"][11]
device_name = devices["device_name"][11]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo de energía durante los fines de semana, 19 y 20 de Junio ~ 35 kWh, 25 de junio ~ 35kWh, 26 de junio ~ 10kWh. Se sugiere validar si existe alguna carga parasitiva que explique este comportamiento.

# ## BC 824 - Ventura Plaza

# In[16]:



device_label = devices["label"][12]
device_name = devices["device_name"][12]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia, consumos nocturnos durante las noches y fines de semana ~ 25 kWh durante el fin de semana del 19 /   20 de junio, ~ 7 kWh durante el 26 de junio

# ## BC 459 - Campo Alegre

# In[17]:




device_label = devices["label"][13]
device_name = devices["device_name"][13]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumos erraticos del aire acondicionado durante todo el periodo monitoreado a excepción de los fines de semana, se sugiere validar si existe alguna carga adicional al aire acondicionado que explique este comportamiento.

# ## BC 306 - Barrancabermeja

# In[18]:




device_label = devices["label"][14]
device_name = devices["device_name"][14]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Cargas residuales no monitoreadas ~ 12 kWh durante las noches, se sugiere validar si existe alguna carga adicional al aire acondicionado que explique este comportamiento.

# ## BC 311 - Bello

# In[19]:




device_label = devices["label"][15]
device_name = devices["device_name"][15]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia

# ## BC 185 - Llano Grande Palmira

# In[20]:




device_label = devices["label"][16]
device_name = devices["device_name"][16]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo de Aire acondicionado constante incluso durante fines de semana, especialmente durante el fin de semana del 20 de junio ~ 90 kWh por día.
# 
# * Circuito de Aire se mantiene encendido durante el 24, 25 y 26 de junio hasta las 9:30 PM aproximadamente

# ## BC 88 - Cúcuta

# In[21]:




device_label = devices["label"][17]
device_name = devices["device_name"][17]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia, consumo de Aire acondicionado representa aproximadamente el 93% del consumo total
# * Consumo de aire durante las noches y fines de semana ~ 12 kWh 

# ## BC 197 - Guatapuri

# In[22]:



device_label = devices["label"][18]
device_name = devices["device_name"][18]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo de aire nocturnos y fines de semana ~ 24 kWh que suman más de 100 kWh durante los fines de semana

# ## BC 78 - El Cacique

# In[23]:



device_label = devices["label"][19]
device_name = devices["device_name"][19]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Sin hallazgos de relevancia

# ## BC 659 - Girardot

# In[24]:




device_label = devices["label"][20]
device_name = devices["device_name"][20]


variable_label = 'aa-potencia-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.rolling(4).mean()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-potencia-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.rolling(4).mean()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-potencia-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.rolling(4).mean()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')


plt.figure(figsize=(10,10))
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Perfil potencia instantánea (kW)")
plt.legend()
plt.tight_layout()



variable_label = 'aa-consumo-activa'
aa =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
aa = aa.resample("1D").sum()
aa =  aa[aa <= aa.quantile(0.95)] 
aa =aa.fillna(method='ffill')

variable_label = 'front-consumo-activa'
front =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
front = front.resample("1D").sum()
front =  front[front <= front.quantile(0.95)] 
front = front.fillna(method='ffill')

variable_label = 'ilu-consumo-activa'
ilu =  Ubidots.Download_from_ubidots(device_label,variable_label,datarange,timestamp_format, token)
ilu = ilu.resample("1D").sum()
ilu =  ilu[ilu <= ilu.quantile(0.95)] 
ilu = ilu.fillna(method='ffill')

consumo = pd.concat([front,aa,ilu],axis=1,join='inner')
consumo["Otros (kWh)"] = consumo["front-consumo-activa"] - consumo["aa-consumo-activa"] - consumo["ilu-consumo-activa"]
consumo.loc['Total'] = consumo.sum(numeric_only=True)
consumo.rename(columns = {'front-consumo-activa':'Frontera (kWh)', 'aa-consumo-activa':'HVAC (kWh)', 'ilu-consumo-activa':'Iluminación (kWh)'},inplace = True)

a = (consumo.div(consumo["Frontera (kWh)"]["Total"])[-1:]*100).rename(index={"Total": "%"})
consumo =consumo.append(a)



plt.figure(figsize=(10,10))
plt.ylim(-10, 595)
plt.plot(aa, label = "Aires")
plt.plot(front, label = "Front")
plt.plot(ilu, label = "ilu")
plt.title(f"{device_name} - Curva de consumo")

plt.tight_layout()
plt.legend()

plt.show()

print(consumo)


# ### **Hallazgos**:
# 
# * Consumo errático durante toda la semana, lo cual representó un incremento de consumo en más de 60%
