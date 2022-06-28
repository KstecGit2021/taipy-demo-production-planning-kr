import numpy as np
import pandas as pd

# this code is used to create the csv file for the demand, it is the source data for the problem

def create_time_series(nb_months=12,mean_A=840,mean_B=760,std_A=96,std_B=72, amplitude_A=108,amplitude_B=144):
    time_series_A = []
    time_series_A.append(mean_A)
    
    time_series_B = []
    time_series_B.append(mean_B)
    
    for i in range(1,nb_months):
        time_series_A.append(np.random.normal(mean_A + amplitude_A*np.sin(2*np.pi*i/12),std_A))
        time_series_B.append(np.random.normal(mean_B + amplitude_B*np.sin((2*np.pi*(i+6))/12),std_B))
        
    time_series_A = pd.Series(time_series_A)
    time_series_B = pd.Series(time_series_B)
    month = [i%12 for i in range(nb_months)]
    year = [i//12 + 2020 for i in range(nb_months)]
    df_time_series = pd.DataFrame({"Year":year,"Month":month,"Demand_A":time_series_A,"Demand_B":time_series_B})
    return df_time_series


def time_series_to_csv(nb_months=12,mean_A=840,mean_B=760,std_A=96,std_B=72, amplitude_A=108,amplitude_B=144):
    time_serie_data = create_time_series(nb_months,mean_A,mean_B,std_A,std_B, amplitude_A,amplitude_B)
    time_serie_data.to_csv('data/time_series_demand.csv')
