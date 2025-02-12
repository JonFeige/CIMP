import pandas as pd
import os
import shutil
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, auc, precision_recall_curve
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("input/results_C.csv")
df = df[df["FP"] + df["TP"] >= 2]
collist = df["Feature"].tolist()

df = pd.read_csv("input/results_J.csv")
utelist = df["Feature"].tolist()

intlist = list(set(collist) & set(utelist))

shutil.rmtree("data")
os.mkdir("data")

df = pd.read_csv("input/results_J.csv", index_col=0)
df = df.loc[intlist]

intlist.append("class")

colrecdata = pd.read_csv('input/mutfeats_C.csv', index_col=0)
#colrecdata = colrecdata[colrecdata["class"] != 2]
colrecdata['class'] = colrecdata['class'].replace([2],-1)
colrecdata = colrecdata[intlist]

utedata = pd.read_csv('input/mutfeats_j.csv', index_col=0)
utedata = utedata[utedata["class"] != 2]
#utedata['class'] = utedata['class'].replace([2],-1)
utedata = utedata[intlist]

df['chi'] = (((df["TP"] - df["TP"].mean()) ** 2) / df["TP"].mean()) + (((df["FP"] - df["FP"].mean()) ** 2) / df["FP"].mean()) + \
    (((df["TN"] - df["TN"].mean()) ** 2) / df["TN"].mean()) + \
    (((df["FN"] - df["FN"].mean()) ** 2) / df["FN"].mean())
df["tp-fp"] = df["TP"] - 2*df["FP"]
fp0 = df[df['FP'] == 0]

#"Pval<0.05", "Pval<0.01", "Pval<0.005", "Chi>3.84", "Chi>7.68", "Chi>15.36", "TP3_FP0", "TP4_FP0", "TP5_FP0"
params = ["Pval<0.05", "Pval<0.01", "Pval<0.005", "Chi>3.84", "Chi>7.68", "Chi>15.36", "TP-2FP>2", "TP-2FP>3", "TP-2FP>4", "FP=0", "TP3_FP0", "TP4_FP0", "All"]


uninonlist = []
runtype = []
for a in params:
    runtype.append([a, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

total = []
totalmean = []
totalruns = 0
crossfold = 11

tf = pd.DataFrame()
remover = 0.0
while tf.empty:
    total = []
    totalmean = []
    for parm in runtype:
        valuelist = []
        fprlist = []
        tprlist = []
        group = []
        group1 = []
        patha = "data/"+str(parm[0])+"/"
        try:
            os.mkdir(patha)
        except:
            shutil.rmtree(patha)
            os.mkdir(patha)
        print(parm[0], '\n')
        for cross in range(crossfold):
            path = patha + "Run_"+str(cross)+"/"
            try:
                os.mkdir(path)
            except:
                shutil.rmtree(path)
                os.mkdir(path)

            datasetc = utedata

            if parm[0] == "FP=0":
                sep = df[df["FP"] == 0]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "FP<=1":
                sep = df[df["FP"] <= 1]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "FP<=2":
                sep = df[df["FP"] <= 2]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()

            if parm[0] == "Pval<0.05":
                sep = df[df["p value"] < 0.05]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "Pval<0.01":
                sep = df[df["p value"] < 0.01]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "Pval<0.005":
                sep = df[df["p value"] < 0.005]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()

            if parm[0] == "Chi>3.84":
                sep = df[df["chi"] > 3.84]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "Chi>7.68":
                sep = df[df["chi"] > 7.68]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "Chi>15.36":
                sep = df[df["chi"] > 15.36]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()

            if parm[0] == "TP-2FP>2":
                sep = df[df["tp-fp"] > 2]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "TP-2FP>3":
                sep = df[df["tp-fp"] > 3]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "TP-2FP>4":
                sep = df[df["tp-fp"] > 4]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()

            if parm[0] == "TP3_FP0":
                sep = fp0[fp0["TP"] > 3]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "TP4_FP0":
                sep = fp0[fp0["TP"] > 4]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()
            if parm[0] == "TP5_FP0":
                sep = fp0[fp0["TP"] > 5]
                muts = sep.index.to_list()
                X = datasetc[muts].to_numpy()

            if parm[0] == "All":
                muts = df.index.to_list()
                X = datasetc[muts].to_numpy()

            ############################################################################################

            y = datasetc['class'].to_numpy()

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=(1/crossfold), train_size=1 - (1/crossfold))

            cancers = ["Uterine", "Colrec"]
            for canc in cancers:
                if canc == "Colrec":
                    X_test = colrecdata[muts].to_numpy()
                    y_test = colrecdata['class'].to_numpy()

                    clf = RandomForestClassifier(oob_score=True, criterion="entropy", n_estimators=1000, max_samples=0.7, max_features=10, max_depth = 10)
                    clf.fit(X_train, y_train)
                    y_pred = clf.predict(X_test)
                    probl = clf.predict_proba(X_test)
                    probr = clf.predict_proba(X_test)

                    predicted = []
                    for x in range(len(y_test)):
                        correct = 0
                        if y_test[x] == y_pred[x]:
                            correct = 1
                        predicted.append([y_test[x], y_test[x],y_pred[x], probl[x][0], probr[x][1], correct])

                if canc == "Uterine":
                    clf = RandomForestClassifier(oob_score=True, criterion="entropy", n_estimators=1000, max_samples=0.7, max_features=10, max_depth = 10)
                    clf.fit(X_train, y_train)
                    y_pred = clf.predict(X_test)
                    probl = clf.predict_proba(X_test)
                    probr = clf.predict_proba(X_test)

                    predicted = []
                    for x in range(len(y_test)):
                        correct = 0
                        if y_test[x] == y_pred[x]:
                            correct = 1
                        predicted.append([y_test[x], y_test[x],y_pred[x], probl[x][0], probr[x][1], correct])

                # ROC_AUC
                probs = clf.predict_proba(X_test)
                probs = probs[:, 1]
                parm[13] = roc_auc_score(y_test, probs)
                fpr, tpr, thresholds = roc_curve(y_test, probs)

                valuelist.append(parm[13])
                fprlist.append(fpr)
                tprlist.append(tpr)

                # Preciion Recall
                model = LogisticRegression(solver='lbfgs')
                model.fit(X_train, y_train)
                yhat = model.predict_proba(X_test)
                probs = yhat[:, 1]
                precision, recall, _ = precision_recall_curve(y_test, probs)
                parm[14] = auc(recall, precision)


                TP = 0
                FP = 0
                TN = 0
                FN = 0
                for x in predicted:
                    if x[1] == 1 and x[2] == 1:
                        TP += 1
                    if x[1] != 1 and x[2] == 1:
                        FP += 1
                    if x[1] != 1 and x[2] != 1:
                        TN += 1
                    if x[1] == 1 and x[2] != 1:
                        FN += 1

                parm[1] = cross
                parm[2] = TP
                parm[3] = FP
                parm[4] = FN
                parm[5] = TN
                try:
                    parm[6] = (TP + TN) / (TP + FP + TN + FN)
                except:
                    parm[6] = -1
                try:
                    parm[7] = (TP) / (TP + FN)
                except:
                    parm[7] = -1
                try:
                    parm[8] = (TN) / (TN + FP)
                except:
                    parm[8] = -1
                try:
                    parm[9] = (TP) / (TP + FP)
                except:
                    parm[9] = -1
                try:
                    parm[10] = (FN) / (FN + TP)
                except:
                    parm[10] = -1
                try:
                    parm[11] = (FP) / (FP + TP)
                except:
                    parm[11] = -1
                try:
                    parm[12] = (FN) / (FN + TN)
                except:
                    parm[12] = -1

                hold = [parm[0] + ":" + canc, parm[1], parm[2], parm[3], parm[4], parm[5], parm[6], parm[7], parm[8], parm[9], parm[10], parm[11], parm[12], parm[13], parm[14], len(muts)]

                tf = pd.DataFrame(predicted, columns=["Name", "Actual", "Predicted", "Probaility left", "Probaility Right", "Correctly Classified"])
                tf.to_csv(path+'predicted.csv', index=False)

                print(str(cross + 1), "/", crossfold)

                if canc == "Uterine":
                    group1.append(hold)
                else:
                    group.append(hold)
                total.append(hold)

        tf = pd.DataFrame(group, columns=["Seperator Type", "Three-Fold Run", "TP", "FP", "FN", "TN", "Accuracy",
                                        "Sensitivity", "Specificity", "Precision", "Miss Rate", "False discovery rate", "False omission rate", "ROC_AUC", "PR Logistic", "Included Muts"])
        tf.to_csv(patha + 'group_stats.csv', index=False)
        tf = tf.drop("Seperator Type", 1)
        tf = tf.drop("Three-Fold Run", 1)
        tfmean = tf.mean().values.tolist()
        totalmean.append([parm[0] + " : ColRec"] + tfmean)


        tf = pd.DataFrame(group1, columns=["Seperator Type", "Three-Fold Run", "TP", "FP", "FN", "TN", "Accuracy", "Sensitivity", "Specificity", "Precision", "Miss Rate", "False discovery rate", "False omission rate", "ROC_AUC", "PR Logistic", "Included Muts"])
        tf.to_csv(patha + 'group1_stats.csv', index=False)

        tf = tf.drop("Seperator Type", 1)
        tf = tf.drop("Three-Fold Run", 1)
        tfmean = tf.mean().values.tolist()
        totalmean.append([parm[0] + " : Uterine"] + tfmean)

        totalruns += 1
        print("\n")
        print(str(totalruns), "/", len(runtype))

        print("############################################\n")

    tf = pd.DataFrame(total, columns=["Seperator Type", "Three-Fold Run", "TP", "FP", "FN", "TN", "Accuracy",
                                    "Sensitivity", "Specificity", "Precision", "Miss Rate", "False discovery rate", "False omission rate", "ROC_AUC", "PR Logistic", "Included Muts"])
    tf.to_csv('total_stat.csv', index=False)

    tf = pd.DataFrame(totalmean, columns=["Seperator Type", "TP", "FP", "FN", "TN", "Accuracy", "Sensitivity",
                                        "Specificity", "Precision", "Miss Rate", "False discovery rate", "False omission rate", "ROC_AUC", "PR Logistic",  "Included Muts"])
    tf.to_csv('total_mean.csv', index=False)

    tf = tf[tf["Accuracy"] >= 0.50 - remover]
    
    remover += 0.002
    totalruns = 0
    print(0.8 - remover, "\n\n")