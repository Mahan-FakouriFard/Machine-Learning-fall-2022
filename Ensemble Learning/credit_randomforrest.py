# -*- coding: utf-8 -*-
"""credit_randomforrest.ipynb

@author: Mahan

"""

import statistics
import math
import pandas as pd
import numpy as np
from numpy import log
from pprint import pprint
import matplotlib.pyplot as plt

from google.colab import drive
drive.mount('/content/gdrive',force_remount=True)

def branches(df,columns):
    att_barnches={}
    for att in columns:
        x=df[att].unique()
        att_barnches[att]=x.tolist()
    return(att_barnches)

def entropy_H_GI(fraction, H_M_GI):
    if fraction==0:
        entropy=0
        # print('xxxx entropy is ', entropy)
    elif H_M_GI == 'H':
        entropy= -(fraction)*math.log(fraction)
    elif H_M_GI == 'GI':
        entropy= -(fraction)**2
    return entropy

def IG(df, att, H_M_GI):
    label_vars =df.label.unique()

    #entropy of whole:
    entropy_s=0
    list_M_S=[]
    for labels in label_vars:
        # num= len(df['label'][df.label== labels])
        num=df.loc[df['label']==labels]['weight'].sum()
        num=round(num,8)
        # den = len(df.label)
        den=df.loc[:,'weight'].sum()
        den=round(den,8)
        # print('den', den , 'num', num , labels)
        if num==0 or den==0:
            frac_s=0
        else:
            frac_s=(num/(den))
        #print(num,den)
        if H_M_GI == 'M':
            list_M_S.append(frac_s)
        else:
            entropy_s += entropy_H_GI(frac_s, H_M_GI)
            # print('entropy_s',entropy_s,'\n')
    if H_M_GI == 'GI':
        entropy_s= 1+entropy_s
    if H_M_GI == 'M':
        entropy_s= 1-max(list_M_S)
    # print('entropy_s',entropy_s)    
    # if entropy_s<0 :
        # print(df)

    #entropy of each attribute:
    features=df[att].unique()
    entropy_sigma=0
    #loop over features of each attribute including [job,age,...]
    for feat in features:
        entropy_att=0
        # M
        if H_M_GI == 'M':
            list_M=[]
            #loop over labels of each features to find majority
            for label_var in label_vars:
                # num = len(df[att][df[att]==feat][df.label ==label_var2])
                df_temp=df.loc[df[att]==feat]
                num=df_temp.loc[df_temp.label ==label_var]['weight'].sum()
                num=round(num,8)
                # den = len(df[att][df[att]==feat]) 
                den=df.loc[df[att]==feat]['weight'].sum()
                den=round(den,8)
                if den==0:
                    frac=0
                else:
                    frac = num/(den)
                list_M.append(frac)
                #print(list_M)
            entropy_att = 1-max(list_M)
            
        # H or GI :
        else:
            #loop over labels of each features 
            for label_var in label_vars:
                # num= len(df[att][df[att]==feat][df.label ==label_var])
                df_temp=df.loc[df[att]==feat]
                num=df_temp.loc[df_temp.label ==label_var]['weight'].sum()
                num=round(num,8)
                
                # den = len(df[att][df[att]==feat]) 
                den=df.loc[df[att]==feat]['weight'].sum()
                den=round(den,8)
                # print( 'feat', feat ,'label_var\n',label_var,'num', num ,'den',den)
                # print("\n")
                if num==0 or den==0:
                    frac=0
                else:
                    frac = num/(den)
                entropy_att += entropy_H_GI(frac,H_M_GI)
            #Gini Index:
            if H_M_GI == 'GI':
                entropy_att= 1+entropy_att
                
        #sum entropy of a feature
        frac_sigma = den/len(df)
        entropy_sigma += frac_sigma*entropy_att
        # print('entropy of',feat, entropy_att,frac_sigma)
    InformationGain = entropy_s- entropy_sigma
    # print('InformationGain',InformationGain,'\n')
    return InformationGain

def choose_node (IG_dict):
    max_IG=0
    #print(IG_dict)
    for attribute in IG_dict:
        if max_IG<=IG_dict[attribute]:
            max_IG=IG_dict[attribute]
            choosen=attribute
        # else:
        #     print(attribute,IG_dict[attribute])
        
    return choosen

def subtable (df,node,branch):
    df_sub=(df[df[node]==branch].reset_index(drop=True))
    return df_sub

def common_func(df):
    x=df.label.unique()
    weight1=df.loc[df['label']==x[0]]['weight'].sum()
    weight2=df.loc[df['label']==x[1]]['weight'].sum()
    if weight1>weight2:
        return x[0]
    else:
        return x[1]

def ID3_func(df,depth,H_M_GI,att_barnches,remain_att,feature_subset,main_tree=None,tree=None): 
    # attributes=[]
    # attributes= df.keys()[:-2]
    
    if len(df.label.unique())==1 and main_tree==None:
        return df.label[0] 
    
    if depth == 0 and main_tree==None:
        common_label= common_func(df)
        return common_label
    #collecting IG of attributes
    else:
        IG_dict={}
        # print(remain_att)
        if len(remain_att)>feature_subset:
            # random_att=remain_att.sample(5,replace=False,axis=0)
            random_att = np.random.choice(remain_att, size=feature_subset, replace=False)
            # print(random_att)
        else:
            random_att=remain_att
        for att in random_att:
            inf_gain = IG(df, att, H_M_GI)
            IG_dict[att]=inf_gain
        #print(IG_dict)
        
        #finding the node 
        root_node=choose_node(IG_dict)
        remain_att=remain_att.drop(root_node)
        #draw tree
        if tree is None:
            tree={}
            tree[root_node]={}
            
        #check the depth and main_tree  
        if depth == 0 and main_tree==True:
            tree[root_node]=common_func(df)
            return tree
        
        depth=depth-1

        #finding subtable
        node_branches=[]
        node_branches=att_barnches[root_node]
        for branch in node_branches:
            df_sub= subtable (df,root_node,branch)
            #print(branch)
            if len (df_sub) == 0:
                tree[root_node][branch]=common_func(df)
            else:
                tree[root_node][branch] =ID3_func(df_sub,depth,H_M_GI,att_barnches,remain_att,feature_subset)
            
    return tree

def predict(tree, df_row,max_depth):
    for key1 in tree.keys():
        if type(tree[key1]) is not dict:
            predict_label=tree[key1]
            return predict_label
        else:
            tree2=tree[key1]
            for key2 in tree2.keys():
                if type(tree2[key2]) is not dict:
                    if df_row[key1]== key2:
                        predict_label =tree2[key2]
                else:
                    if df_row[key1]==key2:
                        tree3=tree2[key2]
                        predict_label=predict(tree3, df_row, max_depth)
    return predict_label

def test(df,tree,max_depth):
    right=0
    for row in range (0,df.shape[0]):
         #print(row)
         df_rows = df.iloc[row , : ]
         #print(df_rows)
         pr_label= predict(tree,df_rows,max_depth)
         #print(pr_label)
         if pr_label==df_rows.label:
             right+=1
    error=(df.shape[0]-right)/df.shape[0]
    return  error

def data_modify(df,linear_att):
    for col in linear_att:
        print(col)
        df=df.astype({col: 'int64'})
        med= df.loc[:,col].median(skipna=False)
        # print(med)
        # print(col,med)
        for row in range(0,df.shape[0]):
            # print("row", row, type(df.loc[row,col]))
            if (df.loc[row,col])<med:
                df.loc[row,col]=0
            else:
                df.loc[row,col]=1
    df=df.replace({'label':0.0},-1.0)
    
            # df= df.astype({'label': 'int32'})
    # print (df)
    return df

def randomforrest(T, df_train,df_test, max_depth, Entropy_method,att_barnches,feature_subset):
    #train
    H_test=np.zeros(df_test.shape[0])
    H_train=np.zeros(df_train.shape[0])
    error_test_list=[]
    error_train_list=[]
    for t in range(1,T+1):
        remain_att=[]
        remain_att=df_train.keys()[:-2] 
        #sampling
        df_new=df_train.sample(df_train.shape[0],replace=True,axis=0)
        df_new=df_new.reset_index(drop=True)
        #finding tree
        tree=ID3_func(df_new, max_depth, Entropy_method,att_barnches,remain_att,feature_subset,main_tree=True)
    #test
        correct_test=0
        for row in range (0,df_test.shape[0]):
          df_rows = df_test.iloc[row , : ]
          #predict bagging
          h=predict(tree, df_rows,max_depth)
          H_test[row]= H_test[row] + h
          pr_label=int(np.sign(H_test[row]))
          if pr_label==0:
              pr_label=+1
          #error_test bagging
          if pr_label==df_rows.label:
              correct_test+=1
        error_test=(df_test.shape[0]-correct_test)/df_test.shape[0]
        print ("T", t , 'error_test', error_test,'\n')
        error_test_list.append(error_test)
        correct_train=0
        for row in range (0,df_train.shape[0]):
          df_rows = df_train.iloc[row , : ]
          #predict bagging
          h=predict(tree, df_rows,max_depth)
          H_train[row]= H_train[row] + h
          pr_label=int(np.sign(H_train[row]))
          if pr_label==0:
              pr_label=+1
          #error_test bagging
          if pr_label==df_rows.label:
              correct_train+=1
        error_train=(df_train.shape[0]-correct_train)/df_train.shape[0]
        
        error_train_list.append(error_train)
        print ("T", t , 'error_train', error_train,'\n')
 
    return error_train_list, error_test_list

#Main body
columns=[ 'LIMIT_BAL','SEX','EDUCATION','MARRIAGE','AGE',
         'PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6',
         'BILL_AMT1','BILL_AMT2','BILL_AMT3','BILL_AMT4','BILL_AMT5','BILL_AMT6',
         'PAY_AMT1','PAY_AMT2','PAY_AMT3','PAY_AMT4','PAY_AMT5','PAY_AMT6','label']

linear_att=['LIMIT_BAL','AGE', 'BILL_AMT1','BILL_AMT2','BILL_AMT3','BILL_AMT4','BILL_AMT5','BILL_AMT6',
            'PAY_AMT1','PAY_AMT2','PAY_AMT3','PAY_AMT4','PAY_AMT5','PAY_AMT6']

data=[]    
tree={}
#train
train_file= open ( 'credit_card_clients.csv' , 'r' )
for line in train_file: 
    terms= line.strip().split(',')
    data.append (terms)
data[0][0]=20000
df= pd.DataFrame(data,columns=columns,dtype=np.float64)
# df=pd.read_csv('credit_card_clients.csv' ,names=columns,dtype=np.float64())
df_modified=data_modify(df,linear_att)

choosen=[]
df_train_m=df_modified.sample( 24000 ,replace=False,axis=0)
df_train_m=df_train_m.reset_index(drop=True)
print(df_train_m)
choosen=df_train_m.index
print(choosen)
df_test_M=df_modified.drop(choosen, axis=0)
df_test_M=df_test_M.reset_index(drop=True)
print(df_test_M)


# #modify with unknown
# df_test_M=data_modify(df_test)

#adding weight to dataset
df_train_m.insert(len(df_train_m.columns),'weight',1)    

#finding attribute branches
att_barnches=branches(df_train_m,columns)

#hyperparameters
max_depth=16
Entropy_method='H'
T=200
feature_subset=2

error_test, error_train=randomforrest(T, df_train_m,df_test_M, max_depth, Entropy_method,att_barnches,feature_subset)
