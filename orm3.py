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

#object was a result id
class EnrichmentResult(object):
    #you will have to account for multiple graphs here
	"""EnrichmentResult: object for documents in the userResults collection"""
	projection = {'_id':0}
	default_score = 0.

	def __init__(self, rid):
		'''To retrieve a result using _id'''
		self.rid = ObjectId(rid)
		doc = COLL_RES.find_one({'_id': self.rid}, self.projection)
		self.data = doc['data']
		self.result = doc['result']
		self.type = doc['type']

	def bind_to_graph(self, df):
		'''Bind the enrichment results to the graph df'''
		df['scores'] = self.result['scores']
		return df
#object used to be 2dict pairs for upgenes and downgenes
class UserInput(object):
	"""The base class for GeneSets and Signature"""

	default_score = 0. # default enrichment score for an irrelevant signature

	def __init__(self, data):
		self.data = data  #one element dict for upgenes
		self.result = None
		self.type = None
		self.rid = None
		self.genelistnames=['TFgenesets.txt','CellTypesgenesets.txt','Ontologygenesets.txt','Diseasesgenesets.txt']
#
	def enrich(self):
        #result is a dictionary of graph# to dict pairs
    	self.resultdict={} 
    	for i in genelistnames:            
        		fisherresponse=Fisher(self.data,i) 
        		fisherresponse=fisherresponse.fishertest()    
        		result=pd.DataFrame(fisherresponse) 
        		# Get the top N as list of records:
        		topn = {
        			'similar': result.iloc[:50].to_dict(orient='records')
        			}
        		# Sort scores by sig_ids to ensure consistency with the graph
        		result.sort_values(by='sig_ids', inplace=True, ascending=True)
        		self.result = {
        			'scores': result['scores'].tolist(), 
        			'topn': topn
        			}
        		self.resultdict[i]=self.result
        return self.resultdict
    
	def save(self): #can still use this for the most part
		'''Save the UserInput as well as the EnrichmentResult to a document'''
		res = COLL_RES.insert_one({
			'result': self.result, 
			'data': self.data, 
			#'type': self.type,
			})
		self.rid = res.inserted_id # <class 'bson.objectid.ObjectId'>
		return str(self.rid)
#
#	def bind_enrichment_to_graph(self, net):
#		'''Bind the enrichment results to the graph df'''
#		df['scores'] = self.result['scores']
#		return df


class Fisher(object):
    def __init__(self,data,genelistname):
        self.data=data
        #convert file into dict of [sig id: list(geneset)] pairs
        # taken from https://stackoverflow.com/questions/17714571/creating-a-dictionary-from-a-txt-file-using-python
        self.genesetdict={}
        with open(genelistname,'r') as f:
            for line in f:
                spl=line.split()
                key=spl[0]
                li=[]
                for i in spl[1:]:
                    li.append(i)
                    self.genesetdict[key]=li
    
    def fishertest(self):
        #iterate through dict of sigid:geneset pairs
        #for each append onto new dict, sig id-pvalue pair
        #return dict 
        newdict={}
        for (k,v) in self.genesetdict.items():
                #use from http://blog.nextgenetics.net/?e=16
            intersection=list(set(data)&set(v))
            intersection=len(intersection)
            user=len(data)
            genelist=len(v)
            total=25000
            #use from https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.fisher_exact.html
            oddsratio, pvalue=stats.fisher_exact([[total,user],[genelist,intersection]])
            newdict[k]=pvalue
        return newdict 


class GeneSets(UserInput):
	"""docstring for GeneSets"""
	def __init__(self, up_genes):
		data = {'upGenes': up_genes}
		UserInput.__init__(self, data)
		self.type = 'geneSet'

	def json_data(self):
		'''Return an object to be encoded to json format'''
		return self.data
