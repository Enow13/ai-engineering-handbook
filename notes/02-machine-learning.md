# Machine Learning – Complete Developer Study Notes 📈🤖

> Every GenAI system still depends on classic ML ideas: data splits, evaluation metrics, overfitting, and features. Master these and every other topic gets easier.

[⬅ Previous: AI Fundamentals](01-ai-fundamentals.md) | [🏠 Home](../README.md) | [Next: Deep Learning ➡](03-deep-learning-and-transformers.md)

## 📚 What's covered

✅ [Supervised, unsupervised & reinforcement learning](#1-the-three-types-of-learning)
✅ [The ML workflow step by step](#2-the-ml-workflow)
✅ [Core algorithms and when to use them](#3-core-algorithms-cheat-sheet)
✅ [Train / validation / test splits & cross-validation](#4-splitting-data-correctly)
✅ [Overfitting, underfitting & the bias–variance trade-off](#5-overfitting-underfitting-biasvariance)
✅ [Evaluation metrics (classification & regression)](#6-evaluation-metrics)
✅ [Feature engineering & preprocessing](#7-feature-engineering)
✅ [Hyperparameter tuning](#8-hyperparameter-tuning)
✅ [A complete scikit-learn example](#9-complete-example-scikit-learn)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** data scientists, ML engineers, AI engineers, and anyone preparing for ML interviews.

---

## 1. The three types of learning

| Type | Data | Goal | Examples |
|---|---|---|---|
| **Supervised** | Inputs **with** labels | Predict the label | Classification (spam?), regression (price) |
| **Unsupervised** | Inputs **without** labels | Find structure | Clustering customers, anomaly detection, dimensionality reduction |
| **Reinforcement** | Rewards from an environment | Learn actions that maximise reward | Game playing, robotics, RLHF for LLMs |
| *Self-supervised* | Labels made from the data itself | Learn representations | LLM pre-training (predict the next word) |

## 2. The ML workflow

```
1. Define the problem & success metric      (business KPI → ML metric)
2. Collect & understand data               (EDA: distributions, missing values, leakage)
3. Prepare data                            (clean, encode, scale, split)
4. Train baseline model                    (simple first: logistic regression / tree)
5. Evaluate on validation data             (right metric for the problem)
6. Improve                                 (features, algorithms, hyperparameters)
7. Final test on held-out test set         (once!)
8. Deploy, monitor, retrain                (MLOps)
```

## 3. Core algorithms cheat sheet

| Algorithm | Type | Use when | Watch out for |
|---|---|---|---|
| **Linear regression** | Regression | Relationship is roughly linear; need interpretability | Outliers, multicollinearity |
| **Logistic regression** | Classification | Strong, explainable baseline | Non-linear patterns |
| **Decision tree** | Both | Need explainable rules | Overfits easily |
| **Random forest** | Both (ensemble, bagging) | Solid default for tabular data | Slower, less interpretable |
| **Gradient boosting** (XGBoost, LightGBM, CatBoost) | Both (ensemble, boosting) | **Best accuracy on tabular data** most of the time | Needs tuning; can overfit |
| **k-Nearest Neighbours** | Both | Small data, similarity-based problems | Slow at scale; needs scaling |
| **SVM** | Both | Medium data, clear margins | Scales poorly to big data |
| **Naive Bayes** | Classification | Text classification baseline | Assumes independent features |
| **k-Means** | Clustering | Group similar items | Choose k; sensitive to scale |
| **DBSCAN** | Clustering | Odd-shaped clusters, outliers | Parameter sensitive |
| **PCA** | Dimensionality reduction | Compress features, visualise | Components are hard to interpret |
| **Isolation Forest** | Anomaly detection | Fraud, intrusion detection | Contamination parameter |

**Bagging vs boosting:** bagging trains many models **in parallel** on random samples and averages them (reduces variance; random forest). Boosting trains models **in sequence**, each fixing the previous one's errors (reduces bias; XGBoost).

## 4. Splitting data correctly

| Split | Typical size | Used for |
|---|---|---|
| **Train** | 60–80% | Fitting the model |
| **Validation** | 10–20% | Choosing models and hyperparameters |
| **Test** | 10–20% | Final, one-time, unbiased estimate |

- **Stratified split:** keeps the class ratio the same in every split (important for imbalanced data).
- **k-fold cross-validation:** split into k folds, train on k-1 and validate on 1, rotate, average the scores. More reliable for small data.
- **Time-series split:** never shuffle. Train on the past, validate on the future.
- ⚠️ **Data leakage:** information from the test set (or the future) sneaks into training, for example scaling **before** splitting, or using a feature only known after the outcome. It gives great offline scores and poor production results.

## 5. Overfitting, underfitting, bias–variance

| | Underfitting | Good fit | Overfitting |
|---|---|---|---|
| Train score | Low | High | Very high |
| Validation score | Low | High | Much lower than train |
| Cause | Model too simple (high **bias**) | | Model too complex / too little data (high **variance**) |
| Fix | More features, more complex model, less regularisation | | More data, regularisation (L1/L2, dropout), simpler model, early stopping, cross-validation |

## 6. Evaluation metrics

### Classification: the confusion matrix

```
                    Predicted +      Predicted -
Actual +            TP               FN   (missed)
Actual -            FP (false alarm) TN
```

| Metric | Formula | Use when |
|---|---|---|
| **Accuracy** | (TP+TN) / all | Classes are balanced |
| **Precision** | TP / (TP+FP) | False positives are costly (spam filter blocking real email) |
| **Recall** (sensitivity) | TP / (TP+FN) | False negatives are costly (cancer screening, fraud) |
| **F1 score** | 2·P·R / (P+R) | You need a balance of precision and recall; imbalanced data |
| **ROC-AUC** | Area under TPR-vs-FPR curve | Ranking quality across all thresholds |
| **PR-AUC** | Area under precision–recall curve | Heavily imbalanced data |
| **Log loss** | Penalises confident wrong probabilities | Probability quality |

### Regression

| Metric | Meaning |
|---|---|
| **MAE** | Average absolute error. Easy to explain, robust to outliers |
| **MSE / RMSE** | Penalises large errors more. RMSE is in the target's units |
| **R²** | Share of variance explained (1 = perfect) |
| **MAPE** | Average percentage error (avoid when actuals can be 0) |

## 7. Feature engineering

| Task | Techniques |
|---|---|
| Missing values | Drop, impute mean/median/mode, model-based imputation, add an "is_missing" flag |
| Categorical data | One-hot encoding, ordinal encoding, target encoding (watch leakage) |
| Scaling | StandardScaler (mean 0, sd 1), MinMaxScaler (0–1). Needed for kNN, SVM, linear models, neural nets |
| Outliers | Clip, log-transform, robust scalers, or investigate |
| Dates | Day of week, month, holiday flags, time since event |
| Text | TF-IDF, embeddings |
| Imbalanced classes | Class weights, SMOTE oversampling, undersampling, threshold tuning |
| Feature selection | Correlation, feature importance, L1 regularisation, recursive feature elimination |

💡 Put preprocessing **inside a pipeline** so the same steps run in training and in production, and are fitted only on training data.

## 8. Hyperparameter tuning

**Parameters** are learned during training (weights). **Hyperparameters** are set before training (tree depth, learning rate, regularisation strength).

| Method | How | Pros / cons |
|---|---|---|
| **Grid search** | Try every combination | Thorough; slow |
| **Random search** | Random combinations | Faster; usually as good as grid |
| **Bayesian optimisation** | Uses past results to pick the next try | Efficient for expensive models |
| **Early termination** (Bandit, median stopping) | Stops bad trials early | Saves compute |

In the cloud: **Azure ML sweep jobs** and **SageMaker AI automatic model tuning** run trials in parallel on a cluster ([MLOps on Azure](16-mlops-on-azure.md), [MLOps on AWS](17-mlops-on-aws.md)).

## 9. Complete example (scikit-learn)

```python
# pip install scikit-learn pandas
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

df = pd.DataFrame({
    "age": [25, 40, 35, 50, 23, 60, 45, 33, 29, 52] * 20,
    "plan": ["basic", "pro", "pro", "basic", "basic", "pro", "pro", "basic", "basic", "pro"] * 20,
    "monthly_spend": [20, 80, 75, 25, 15, 90, 70, 30, 22, 85] * 20,
    "churned": [1, 0, 0, 1, 1, 0, 0, 1, 1, 0] * 20,
})
X, y = df.drop(columns="churned"), df["churned"]

# 1. Split BEFORE any fitting (prevents leakage), stratified for class balance
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 2. Preprocessing lives inside the pipeline
preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]),
     ["age", "monthly_spend"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan"]),
])
pipe = Pipeline([("prep", preprocess), ("model", HistGradientBoostingClassifier(random_state=42))])

# 3. Hyperparameter tuning with 5-fold cross-validation
search = GridSearchCV(pipe, {"model__max_depth": [3, None], "model__learning_rate": [0.05, 0.1]},
                      cv=5, scoring="f1")
search.fit(X_train, y_train)

# 4. Final, one-time evaluation on the test set
pred = search.predict(X_test)
print("Best params:", search.best_params_)
print(classification_report(y_test, pred))
print("ROC-AUC:", roc_auc_score(y_test, search.predict_proba(X_test)[:, 1]))
```

---

## 💬 Interview questions & answers

**Q1. Precision or recall for fraud detection?**
Usually recall: missing fraud (a false negative) costs more than reviewing a false alarm. In practice you tune the decision threshold to the business cost of each error, and report both, plus PR-AUC because fraud data is imbalanced.

**Q2. Your model has 99% accuracy. Is it good?**
Not necessarily. If only 1% of cases are positive, predicting "negative" every time gives 99% accuracy. Check precision, recall, F1 and the confusion matrix.

**Q3. How do you detect overfitting?**
A big gap between training and validation scores. Fix it with more data, regularisation, a simpler model, early stopping, or cross-validation.

**Q4. What is data leakage? Give an example.**
Information unavailable at prediction time ends up in training. Examples: scaling the whole dataset before splitting, or using "refund_issued" to predict "complaint". Prevent it with pipelines, splitting first, and time-aware splits.

**Q5. Random forest vs gradient boosting?**
Random forest builds independent trees in parallel and averages them, so it's robust with little tuning. Gradient boosting builds trees in sequence, each correcting the previous ones, so it's usually more accurate but needs tuning and can overfit.

**Q6. How do you handle imbalanced data?**
Use the right metrics (F1, PR-AUC), class weights, resampling (SMOTE or undersampling), threshold tuning, and stratified splits.

**Q7. Why scale features?**
Distance- and gradient-based algorithms (kNN, SVM, linear models, neural nets) are dominated by large-scale features otherwise. Tree models don't need scaling.

**Q8. Explain cross-validation.**
Split the training data into k folds, train k times (each time holding out one fold for validation), and average the scores. It gives a more reliable estimate than a single split, especially on small data.

**Q9. Parameters vs hyperparameters?**
Parameters are learned from data (weights, split points). Hyperparameters control learning and are set beforehand (learning rate, depth, number of trees).

---

## ✅ Final revision checklist

- [ ] I can explain supervised, unsupervised, reinforcement and self-supervised learning.
- [ ] I can pick an algorithm for a tabular problem and justify it.
- [ ] I can draw a confusion matrix and compute precision, recall and F1.
- [ ] I can explain overfitting, the bias–variance trade-off, and how to fix each side.
- [ ] I know three causes of data leakage.
- [ ] I can explain grid vs random vs Bayesian search.
- [ ] I can build a scikit-learn pipeline with preprocessing and cross-validation.

## 🔗 Official docs
- scikit-learn user guide: https://scikit-learn.org/stable/user_guide.html
- Google ML crash course: https://developers.google.com/machine-learning/crash-course

---
*My AI Engineering Study Notes* | [⬅ Previous](01-ai-fundamentals.md) | [🏠 Home](../README.md) | [Next ➡](03-deep-learning-and-transformers.md)
