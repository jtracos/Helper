import glob
import os
import pandas as pd
import re
import numpy as np

def obtener_estacion_evento(files):
    """ obtiene el numero de evento y el nombre de la estacion que lo registra sin repetir
    """
    regex = re.compile(r'[A-Za-z]{4}|\d{2,}')
    metadata = [regex.findall(f) for f in files]
    return metadata

def obtener_archivos_componentes(files, metadata):
    """Regresa una lista de listas con los nombres de los 
    archivos que corresponden a la misma estacion y evento
    """
    all = []
    for row in metadata:
        tmp = []
        for f in files:
            if row[0] in f and row[1] in f:
                tmp.append(f)
        all.append(tmp)
    return all


def obtener_amplitud(dfs):
    """une los datos de las componentes, realiza el calculo de la amplitud
    y devuelve el resultado en un dataframe"""
    df_temp = dfs[0].set_index('freq').join(dfs[1].set_index('freq'), how='inner')
    df_temp= df_temp.reset_index(0)
    df_temp['amplitud'] = df_temp.replace(
        {-1.000:0.0}
        ).apply(lambda row: np.sqrt(row[1]**2 + row[2]**2), axis=1)
    df_temp = df_temp.drop(['amp0', 'amp1'], axis = 1)
    return df_temp


def obtener_amplitudes(path, pattern):
    os.chdir(path)
    files_comp = glob.glob('*e-*.txt')
    files = glob.glob('*.txt')
    metadata = obtener_estacion_evento(files_comp)
    componentes = obtener_archivos_componentes(files, metadata)
    for _, comp in enumerate(componentes):#enumerate: para obtener el metadata correspondiente y nombrar el archivo
        dfs = []
        for e,f in enumerate(comp):
            df_ = pd.read_csv(f, skiprows=1, sep='\s+',header=None, names=['freq',f'amp{e}']) 
            dfs.append(df_)
        df_temp = obtener_amplitud(dfs)
        nm = metadata[_][0] + '-' + metadata[_][1]#se guardan con la nomenclatura 'estacion'-'evento's.txt
        df_temp.to_csv(nm+'s.txt',sep=' ', float_format='%.4E')

if __main__ == '__main__':

    path = '/content/'
    obtener_amplitudes(path, '*e-*.txt')