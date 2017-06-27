# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 16:27:34 2017

@author: Charlotte
"""
#python -c 'import foo; print foo.hello()'
import os, sys
import json
import numpy as np
np.random.seed(10)
import requests
import pandas as pd

import re
from werkzeug.routing import Rule, RequestRedirect

from flask import Flask, request, redirect, render_template, send_from_directory, abort, Response
enter_point='/helpme' 
allcyjs=np.array(["diseases_adjmat.txt.gml.cyjs","transcriptionfactors_adjmat.txt.gml.cyjs","celltypes_adjmat.txt.gml.cyjs","ontologies_adjmatfixed.txt.gml.cyjs"])
#"celltypes_adjmat.txt.gml.cjys","ontologies_adjmatfixed.txt.gml.cyjs"])
allmetadata=np.array(["disall1.txt","newmetadata2.txt","celltypeall1.txt","ontologyall1.txt"])
#pp2=Flask(__name__)
app2 = Flask(__name__, static_url_path=enter_point, static_folder=os.getcwd())
#CYJS="transcriptionfactors_adjmat.txt.gml.cyjs"

from orm2 import *

app2.debug=True

#@app2.before_first_request
#def load_globals():
#    global meta_df, graph_df
#    meta_df=pd.read_csv('newmetadata.txt')
#    #cyjs_filename=os.environ['CYJS']
#    cyjs_filename=CYJS
#    graph_df=load_graph(cyjs_filename,meta_df)
#    
#    
#    return

@app2.before_first_request
def load_globals2():
    global metadatalist, graph_df_list 

    cyjslist=[]
    metadatalist=[]
    graph_df_list=[]
    for i in range(allcyjs.size):
        cyjslist.append(allcyjs[i])
        metadatalist.append(pd.read_csv(allmetadata[i]))
    
    for i in range(len(cyjslist)):
        graph_df_list.append(load_graph(cyjslist[i],metadatalist[i]))
    return 

@app2.route(enter_point+'/')
def index_page():
    return render_template('index.html',
        script='main3',
        enter_point=enter_point,
        result_id='hello')  

@app2.route(enter_point + '/graph', methods=['GET'])
def load_graph_layout_coords():
	if request.method == 'GET':
		print graph_df_list[0].shape
		return graph_df_list[0].reset_index().to_json(orient='records')
    
@app2.route(enter_point + '/graph/1', methods=['GET'])
def load_graph_layout_coords2():
	if request.method == 'GET':
       
		graph_test=graph_df_list[1]
		print graph_test.shape
		return graph_test.reset_index().to_json(orient='records')
@app2.route(enter_point+'/graph/2',methods=['GET'])
def load_graph_layout_coords3():
    if request.method=='GET':
        graph_test=graph_df_list[2]
        print graph_test.shape
        return graph_test.reset_index().to_json(orient='records')

@app2.route(enter_point+'/graph/3',methods=['GET'])
def load_graph_layout_coords4():
    if request.method=='GET':
        graph_test=graph_df_list[3]
        print graph_test.shape
        return graph_test.reset_index().to_json(orient='records')

@app2.route(enter_point + '/sig_ids', methods=['GET'])
def get_all_sig_ids():
	if request.method == 'GET':
		cyjs_filename =CYJS #os.environ['CYJS']
		json_data = json.load(open('notebooks/%s' % cyjs_filename, 'rb'))
		json_data = json_data['elements']['nodes']
		sig_ids = [rec['data']['name'] for rec in json_data]
		return json.dumps({'sig_ids': sig_ids, 'n_sig_ids': len(sig_ids)})    
#
@app2.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app2.static_folder,filename)

@app2.route(enter_point + '/search', methods=['POST'])
def post_to_sigine():
	#Endpoint handling signature similarity search, POST the up/down genes 
	#to the RURL and redirect to the result page.
	if request.method == 'POST':
		# retrieve data from the form 
		up_genes = request.form.get('upGenes', '').split()
		#down_genes = request.form.get('dnGenes', '').split()
		# init GeneSets instance
		gene_sets = GeneSets(up_genes)# down_genes)
		# perform similarity search
        #run own function
		result = gene_sets.enrich()
		# save gene_sets and results to MongoDB
		rid = gene_sets.save()
		print rid
		return redirect(enter_point + '/result/' + rid, code=302)
 
#called by new scatterData object    
@app2.route(enter_point + '/result/graph/<string:result_id>', methods=['GET'])
def result(result_id):
	"""
	Retrieve a simiarity search result using id and combine it
	with graph layout.
	"""
	# retrieve enrichment results from db
	result_obj = EnrichmentResult(result_id)
	# bind enrichment result to the network layout
	graph_df_res = result_obj.bind_to_graph(graph_df)

	return graph_df_res.reset_index().to_json(orient='records')


@app2.route(enter_point + '/result/<string:result_id>', methods=['GET'])
def result_page(result_id):
	#The result page.
	
	return render_template('index.html', 
		script='result', 
		ENTER_POINT=enter_point,
		result_id=result_id)
    
    

if __name__ == '__main__':
	app2.run(port=5000, threaded=True)
