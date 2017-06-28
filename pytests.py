

from bson.objectid import ObjectId
from pymongo import MongoClient


client=MongoClient("localhost",27017)
db=client.test
genelistname=Diseasesgenesets.txt
with open(genelistname,'r') as f:
    for line in f:
        print(line)


#res=db.placeholder.insert_one({'hello':[1,2,3]})
#rid=res.inserted_id
#print(rid)

#data = {'data':['ABC','GHI','STU','TUV']} 
#class UserInput(object):
#    def __init__(self,data):
#        self.data=data
#        self.ridlist={}
#        self.resultdict={0:{'scores':[1,2,3,1,2,3],'topn':{'similar':[2,5]}},
#                         1:{'scores':[5,2,3,6,2,3],'topn':{'similar':[0,3]}},
#                         2:{'scores':[1,7,3,1,2,8],'topn':{'similar':[1,5]}}}
#    def save(self):
#        for (k,v) in self.resultdict.items():
#            res=db.placeholder.insert_one({
#                    'result':v,
#                    'data':self.data
#                    })
#            self.ridlist[k]=res.inserted_id
#                        
#        return str(self.ridlist)
#r=UserInput(data)
#print(r.save())    
#
##    def __init__(self,data):
##    		 #one element dict for upgenes given by user
##        self.data=data
##    		#self.result = None
##    		#self.type = None
##        self.ridlist = None
##        self.resultdict={0:{'scores':[1,2,3,1,2,3],'topn':{'similar':[2,5]}},
##                         1:{'scores':[5,2,3,6,2,3],'topn':{'similar':[0,3]}},
##                         2:{'scores':[1,7,3,1,2,8],'topn':{'similar':[1,5]}}}    
##    
##    
##    def save(self): #can still use this for the most part
##    		'''Save the UserInput as well as the EnrichmentResult to a document'''
##            #have to change self.result to self.resultdict
##        for (k,v) in self.resultdict.items()
##            res=db.placeholder.insert_one({
##                'result':v,
##                'data':self.data
##                })
##            self.ridlist[k]=res.inserted_id # <class 'bson.objectid.ObjectId'>
##
##        	
##        #self.ridlist = res.inserted_ids # <class 'bson.objectid.ObjectId'>
##        return str(self.ridlist)
#
##r=UserInput(data)
##print(r.save())