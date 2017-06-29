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
import scipy.stats as stats
from bson.objectid import ObjectId
from pymongo import MongoClient

client=MongoClient('mongodb://146.203.54.131:27017/')
#client=MongoClient('localhost',27017)
db=client.test

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

##object was a result id
class EnrichmentResult(object):
    #you will have to account for multiple graphs here
	"""EnrichmentResult: object for documents in the userResults collection"""
	projection = {'_id':0}
	default_score = 0.

	def __init__(self, rid,graph):
		'''To retrieve a result using _id'''
		self.rid = ObjectId(rid)
		doc = db.placeholder6.find_one({'_id': self.rid}, self.projection)
		self.data = doc['data']
		self.result = doc['result'][str(graph)]

	def bind_to_graph(self, df):
		'''Bind the enrichment results to the graph df'''
		df_ = df.copy()
		df_['scores'] = self.result['scores']
		return df_


class UserInput(object):
	"""The base class for GeneSets and Signature"""

	default_score = 0. # default enrichment score for an irrelevant signature

	def __init__(self, data):
		self.data = data  #one element dict for upgenes given by user
		self.result = {}
		self.ridlist = None
		self.resultdict={}
#
	def enrich(self):
       #dont use v, just dont know how to only look at k 
		for (k,v) in genelistnames.items():
			fisherresponse=Fisher(self.data,k)
			fisherresponse=fisherresponse.fishertest()
          #fisherresponse is now a list
          #will have to change all of this by adding your own col for sigid
          result=pd.DataFrame({'scores':fisherresponse})
          result['sig_id']=range(1,len(fishertest))
			#result=pd.DataFrame(fisherresponse.items(),columns=['sig_id','scores'])
			#result['sig_id']=pd.to_numeric(result['sig_id'])
			result=result.sort_values(['scores'])
			#print(result)
			topn=result.iloc[:50]#.to_dict(orient='records')
			topn=dict(zip(str(topn['sig_id']),topn['scores']))
			#print(topn)
			result=result.sort_values(['sig_id'])
			#print(result)
			self.result={
				'scores':result['scores'].tolist(),
				'topn':topn
				}
			self.resultdict[str(k)]=self.result
		return self.resultdict

    
	def save(self):
		res=db.placeholder6.insert_one({
			'result':self.resultdict,
			'data':self.data
			})
		self.ridlist=res.inserted_id
		return str(self.ridlist)
    

#
#	def bind_enrichment_to_graph(self, net):
#		'''Bind the enrichment results to the graph df'''
#		df['scores'] = self.result['scores']
#		return df


class Fisher(object):
    def __init__(self,data,category):
        self.data=data
        self.genesets=genesetlist[category]

    
    def fishertest(self):
        #learn how to use the empty, set size list!        
        #pvalues = [None] * len(self.geneset)
        pvalues=[]
        for k in self.genesets: #for each gene set
                #use from http://blog.nextgenetics.net/?e=16
            intersection=list(set(self.data)&set(k))
            intersection=len(intersection)           
            user=len(self.data)
            # k is the inner list, each element a gene
            genelist=len(k)
            total=25000
            #use from https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.fisher_exact.html
            oddsratio, pvalue=stats.fisher_exact([[total,genelist],[user,intersection]])
            pvalues.append(pvalue)
              
        return pvalues 


class GeneSets(UserInput):
	"""docstring for GeneSets"""
	def __init__(self, up_genes):
		data = up_genes
		UserInput.__init__(self, data)
		self.type = 'geneSet'

	def json_data(self):
		'''Return an object to be encoded to json format'''
		return self.data
    
    
