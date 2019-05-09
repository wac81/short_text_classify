import xgboost as xgb
# read in data
dtrain = xgb.DMatrix('train.svm.xgboost')
dtest = xgb.DMatrix('test.svm.xgboost')
# specify parameters via map
param = {'num_class':3, 'max_depth':4, 'eta':0.1, 'silent':False,
         'objective':'multi:softmax',
         # 'objective': 'binary:logistic',
         # 'objective': 'binary:hinge'
         # 'objective': 'reg:logistic'

         }
num_round = 20
bst = xgb.train(param, dtrain, num_round)
# make prediction
preds = bst.predict(dtest)

print(preds)
labels = dtest.get_label()
print('error=%f' % (sum(1 for i in range(len(preds)) if preds[i] != labels[i]) / float(len(preds))))