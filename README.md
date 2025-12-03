# Federated Learning with FedAvg and PySyft

A complete implementation of **Federated Learning (FL)** using the **FedAvg** algorithm while preserving data privacy with **PySyft**. This project demonstrates how multiple datasites can collaboratively train machine learning models without sharing raw data.


This project implements federated learning on the **MNIST** dataset, split arbitrarily between two datasites. Each datasite trains a local **Logistic Regression** model on its private MNIST shard, and a central process aggregates the local model parameters using **FedAvg** over several federated rounds.

## Architecture

```
┌──────────────────────────────────────────────┐
│          Central Server (Client)             │
│  - Aggregates model parameters (FedAvg)      │
│  - Orchestrates FL rounds                    │
└──────────────────────────────────────────────┘
          ↓                          ↓
┌──────────────────────┐   ┌──────────────────────┐
│   Datasite 1 (FL)    │   │   Datasite 2 (FL)    │
│  - MNIST shard 1     │   │  - MNIST shard 2     │
│  - Local ML training │   │  - Local ML training │
│  - Privacy preserved │   │  - Privacy preserved │
└──────────────────────┘   └──────────────────────┘
```

**Key features:**
-  No raw data ever leaves the datasites — only model parameters are shared
-  Multiple datasites train independently and locally
-  Central server aggregates parameters using FedAvg
-  Metrics (accuracy, confusion matrices) tracked per round
-  Visualization of convergence across FL epochs

## Main Code

The **main implementation** is located in:
- **`FLPysyftcodeLogisticRegression.ipynb`** — Production-ready code containing:
  - `ml_experiment(data, global_params=None, seed)` — Local training function run on each datasite
  - `avg_params(all_params)` — FedAvg parameter aggregation
  - `fl_experiment_logreg_true(datasites, fl_epochs, seed)` — Main federated learning loop

The notebook `FLPysyftcodeLogisticRegression.ipynb` provides an educational walkthrough of the same concepts with visualizations.

## Installation & Setup



```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
```

### Launch Datasites

Before running the federated learning experiment, start the datasites:

```bash
python launch_datasites.py
```

This will:
- Launch 2 datasites on `http://localhost:54879` and `http://localhost:54880`
- Split MNIST data between them
- Automatically approve incoming code requests
- Display connection information

Expected output:
```
=================================================================
2 DataSites Up and Running.

1. MNIST Part 1: http://localhost:54879
2. MNIST Part 2: http://localhost:54880
=================================================================
```

## Running the Federated Learning Experiment

```bash
jupyter notebook 
```

## How It Works

Each datasite receives:
- Its private MNIST shard (X, y)
- Optionally, the current global model parameters

The function:
1. Splits data into train/test sets
2. Trains a Logistic Regression model
3. Returns metrics (train/test accuracy, confusion matrix)
4. Returns updated model parameters (coef, intercept)


The central server:
1. Collects model parameters from all datasites
2. Averages them element-wise: `global_params = mean([local_params_1, local_params_2, ...])`
3. Updates the global model with the aggregated parameters

For each FL epoch:
1. Distribute current global parameters to each datasite
2. Each datasite trains locally with its data + global parameters
3. Collect local parameters
4. Aggregate using FedAvg
5. Log metrics (accuracy per site per epoch)
6. Repeat



## Results Example

```
=== FL epoch 1/5 ===
  MNIST Part 1 -> train=0.8234, test=0.8121
  MNIST Part 2 -> train=0.8156, test=0.8045
  FedAvg epoch 1: intercept shape=(10,), coef shape=(10, 784)

=== FL epoch 2/5 ===
  MNIST Part 1 -> train=0.8412, test=0.8278
  MNIST Part 2 -> train=0.8367, test=0.8201
  FedAvg epoch 2: intercept shape=(10,), coef shape=(10, 784)

... (epochs 3-5)
```

Final accuracies typically converge to **~82-84%** on test sets.

## Conclusion

This implementation demonstrates a complete end-to-end federated learning pipeline. Multiple datasites train collaboratively on their private MNIST shards, sharing only model parameters (not raw data). The FedAvg algorithm aggregates these local updates into a global model over multiple rounds, and the resulting accuracies and confusion matrices show that it is possible to achieve good model performance while preserving data privacy.

## References & Inspiration

This project is inspired by:
- [OpenMined Blog: A Python Package and an Email is All You Need](https://openmined.org/blog/a-python-package-and-an-email-is-all-you-need/)

Additional references:
- [PySyft Documentation](https://docs.openmined.org/en/latest/)
- [FedAvg Algorithm](https://arxiv.org/abs/1602.05629) (McMahan et al., 2016)
- [MNIST Dataset](http://yann.lecun.com/exdb/mnist/)
- [OpenMined Organization](https://openmined.org/)


