import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)


class ModelTrainer:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        self.X = []
        self.y = []
        self.all_preds = []
        self.all_true = []
        self.metrics_history = []
        self.metrics_file = Path(__file__).parent.parent.parent / 'data' / 'metrics.json'
        
    def update_metrics(self):
        if len(self.all_true) == 0:
            return
        
        metrics = {
            'samples': len(self.all_true),
            'accuracy': accuracy_score(self.all_true, self.all_preds),
            'precision': precision_score(self.all_true, self.all_preds, average='macro'),
            'recall': recall_score(self.all_true, self.all_preds, average='macro'),
            'f1': f1_score(self.all_true, self.all_preds, average='macro'),
            'confusion_matrix': confusion_matrix(self.all_true, self.all_preds).tolist()
        }
        
        self.metrics_history.append(metrics)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f)

    def add_data(self, features, label):
        if label is None:
            return
            
        self.X.append(list(features.values()))
        self.y.append(label)
        
        if len(self.X) >= 1 and self.model.fit_intercept:
            if len(self.X) > 100:
                X = np.array(self.X[-100:])
                y = np.array(self.y[-100:])
            else:
                X = np.array(self.X)
                y = np.array(self.y)
                
            self.model.fit(X, y)
            
            preds = self.model.predict(X)
            self.all_preds.extend(preds)
            self.all_true.extend(y)
            
            self.update_metrics()
