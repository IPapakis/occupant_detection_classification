import csv
import argparse
import os
from sklearn import metrics
from sklearn.metrics import roc_auc_score
from matplotlib import pyplot
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc
from sklearn.metrics import confusion_matrix
import seaborn as sns
import json

sns.set_style('whitegrid')
parser = argparse.ArgumentParser()
parser.add_argument('--det',type=str) #give path to detection files
parser.add_argument('--gt',type=str) #give path to ground truth files
args = parser.parse_args()

front_ground_truth= []

for root, dirs, files in os.walk(args.gt):
    if not files:
        continue
    files.sort()
    for f in files:
        if f.endswith('.json'):
            with open(args.gt+f) as json_file:
                loaded_data = json.load(json_file)
                
front_pred_res= []
vertical_limit= 240
horizontal_limit= 360
bbox_area_limit= 30000
for root, dirs, files in os.walk(args.det):
    if not files:
        continue
    prefix = os.path.basename(root)
    files.sort()
    for f in files:
        if f.endswith('.txt'):
            for p in loaded_data['images']:
                if os.path.splitext(f)[0]==p['file_name'] and f[-7:-4]=='Day':
                    front_found= False
                    image_id= p['id']
                    for p2 in loaded_data['annotations']:
                        if p2['image_id']==image_id:
                            if p2['category_id']==3:
                                front_found = True
                    if front_found==False:
                        front_ground_truth.append(0)
                    else:
                        front_ground_truth.append(1)
                    with open(os.path.join(root, f)) as txt_file:
                        prob= []
                        for line in txt_file:
                            type= line.split()[0]
                            xmin = float(line.split()[2])
                            ymin = float(line.split()[3])
                            xmax = float(line.split()[4])
                            ymax = float(line.split()[5])
                            conf = float(line.split()[1])
                            bbox_area= (xmax-xmin)*(ymax-ymin)
                            x= (xmin+xmax)/2
                            y= (ymin+ymax)/2
                            if bbox_area>bbox_area_limit and x<horizontal_limit and y>vertical_limit:
                                prob.append(conf)
                    temp = 1
                    for j in prob:
                        temp *= (1-j)
                    final_prob= (1-temp)
                    front_pred_res.append(final_prob)
                    break
# confusion matrix
print('front')
limit= 0.97
yconf= []
for i in front_pred_res:
    if i<limit:
        yconf.append(0)
    else:
        yconf.append(1)
tn, fp, fn, tp = confusion_matrix(front_ground_truth, yconf).ravel()
acc= (tp+tn)/(tn+ fp+ fn+ tp)
print("True Positives: "+str(tp))
print("True Negatives: "+str(tn))
print("False Positives: "+str(fp))
print("False Negatives: "+str(fn))
print("Accuracy: "+str(acc))

# # Optional 
# # f1 score
# pr_f1 = f1_score(front_ground_truth, yconf)
# print('PR curve max F1: %.3f' %(pr_f1))
# # calculate AUC
# roc_auc = roc_auc_score(front_ground_truth, front_pred_res)
# print('ROC curve AUC, driver: %.3f' % roc_auc)
# # roc curve
# fpr1, tpr1, thresholds1 = metrics.roc_curve(front_ground_truth, front_pred_res, pos_label=1)
# pyplot.plot(fpr1, tpr1, marker='.')
# pyplot.xlabel('False Positive Rate', **{'size':'14'})
# pyplot.ylabel('True Positive Rate', **{'size':'14'})
# pyplot.savefig('ROC_front_day.png')
# pyplot.close()