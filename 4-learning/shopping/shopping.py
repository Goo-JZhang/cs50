import csv
import sys
import ipdb

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4

def main():

    # Check command-line arguments
    #print(sys.argv)
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    typesort = {'Administrative':'int', 'Informational':'int','ProductRelated':'int','OperatingSystems':'int'
                ,'Browser':'int','Region':'int','TrafficType':'int',
                'Administrative_Duration':'float','Informational_Duration':'float','ProductRelated_Duration':'float',
                'BounceRates': 'float', 'ExitRates': 'float','PageValues':'float','SpecialDay':'float',
                'Weekend':'bool','Month':'month','VisitorType':'type',
                'Revenue':'label'}
    m2int = {'Jan':0, 'Feb':1, 'Mar':2, 'Apr':3,'May':4,'June':5,'Jul':6,'Aug':7,'Sep':8,'Oct':9,'Nov':10,'Dec':11}
    evidences = []
    labels = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence = []
            for key in row:
                if typesort[key]=='int':
                    evidence.append(int(row[key]))
                elif typesort[key]=='float':
                    evidence.append(float(row[key]))
                elif typesort[key]=='bool':
                    if row[key]=='TRUE':
                        evidence.append(1)
                    else:
                        evidence.append(0)
                elif typesort[key]=='month':
                    evidence.append(m2int[row[key]])
                elif typesort[key]=='type':
                    if row[key]=='Returning_Visitor':
                        evidence.append(1)
                    else:
                        evidence.append(0)
                elif typesort[key]=='label':
                    if row[key]=='FALSE':
                        labels.append(0)
                    else:
                        labels.append(1)
                else:
                    raise KeyError("Invalid keys")
                #ipdb.set_trace()
            evidences.append(evidence)
    return evidences,labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    knc = KNeighborsClassifier(n_neighbors = 10)
    knc.fit(evidence,labels)
    return knc


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    N = len(labels)
    for i in range(N):
        if predictions[i]==1:
            if labels[i]==1:
                TP += 1
            else:
                FP +=1
        if predictions[i]==0:
            if labels[i]==1:
                FN += 1
            else:
                TN +=1
    return (TP/(TP + FP),TN/(TN + FN))


if __name__ == "__main__":
    main()
