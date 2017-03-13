'''
Compute PCA coordinates for CD signatures.
'''

import os
import h5py
import math

import numpy as np
import pandas as pd
from sklearn import decomposition
from sqlalchemy import create_engine

f = h5py.File('data/CD_matrix_45012xlm978.h5', 'r')
mat = f['matrix']
sig_ids = f['meta']['sig_ids']
print mat.shape, type(mat), len(sig_ids)

# 0) Create metadata.tsv
engine = create_engine("mysql://euclid:elements@amp.pharm.mssm.edu:3306/euclid3?charset=utf8")
meta_df = pd.read_sql('optional_metadata', engine, columns=['gene_signature_fk', 'name', 'value'])
meta_df = pd.pivot_table(meta_df, values='value', 
	columns=['name'], index=['gene_signature_fk'], aggfunc=lambda x:x)
# print meta_df.head()
# print meta_df.shape

meta_df = meta_df.reset_index().set_index('sig_id').drop(['gene_signature_fk', 'disease', 'gene'], axis=1)
# print meta_df.head()

# find shared sig_ids
sig_ids_shared = list(set(list(sig_ids)) & set(meta_df.index))
print '# shared sig_ids: %d' % len(sig_ids_shared)
mask_shared = np.in1d(list(sig_ids), sig_ids_shared)
sig_ids_shared = np.array(sig_ids)[mask_shared]
print 'mask_shared.shape:', mask_shared.shape

# subset and reorder
meta_df = meta_df.ix[sig_ids_shared]
print meta_df.head()
print meta_df.shape

print meta_df['cell'].nunique()
print meta_df['pert_id'].nunique()
print meta_df['perturbation'].nunique()
meta_df.to_csv('data/metadata.tsv', sep='\t')

mat = mat[mask_shared,:]
print mat.shape

batch_size = 400
ipca = decomposition.IncrementalPCA(n_components=3, batch_size=None)

n_batchs = int(math.ceil(len(sig_ids_shared) / float(batch_size)))

for i in range(n_batchs):
	start_idx = i * batch_size
	end_idx = (i+1) * batch_size

	ipca.partial_fit(mat[start_idx:end_idx])

mat_coords = np.zeros((len(sig_ids_shared), 3))
for i in range(n_batchs):
	start_idx = i * batch_size
	end_idx = (i+1) * batch_size

	mat_coords[start_idx:end_idx] = ipca.transform(mat[start_idx:end_idx])

np.save('data/pca_coords', mat_coords)


