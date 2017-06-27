# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 08:30:58 2017

@author: Charlotte
"""

import os
import json, requests
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def load_graph(cyjs_filename,meta_df): 
	json_data=json.load(open('notebooks/%s' %cyjs_filename, 'rb'))
	json_data=json_data['elements']['nodes']
    
	scl=MinMaxScaler((-10,10))
    
	coords=np.array([
            [rec['position']['x'] for rec in json_data],
            [rec['position']['y'] for rec in json_data]
            ]).T
	coords=scl.fit_transform(coords)
    
	df = pd.DataFrame({
		'sig_id': map(int,[rec['data']['name'] for rec in json_data]),
		'x': coords[:, 0],
		'y': coords[:, 1],
		}).set_index('sig_id')
	df['z'] = 0
	df = df.merge(meta_df, how='left',left_index=True,right_index=True)
	#df['neglogp'] = -np.log10(df['pvalue']+1e-4)
    
	df = df.sort_index()
	return df
