# Satellite Collision Risk AI (Time-Series LSTM)

A sophisticated machine learning system that predicts satellite collision risk by analyzing the *evolution* of Conjunction Data Messages (CDMs) over time. Unlike traditional snapshot-based approaches, this system uses a Long Short-Term Memory (LSTM) network to model how risk parameters (Probability, Miss Distance, etc.) change as the Time of Closest Approach (TCA) nears.

## 🚀 Key Features

- **Time-Series Analysis**: Groups multiple CDM updates for the same event to form a sequence.
- **LSTM Deep Learning**: Uses PyTorch to capture temporal dependencies and risk trajectories.
- **Certainty Quantification**: Estimates model confidence using Monte Carlo Dropout.
- **JSON Data Support**: Natively processes `CDM_public` JSON formats.
- **Configurable Pipeline**: Easy adjustment of sequence length, model size, and training parameters via `config.yaml`.

## 📦 Installation

### Prerequisites
- Python 3.8+
- PyTorch 2.0+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ra-xor/collision-risk-ai-mostafa-fork.git
cd collision-risk-ai-mostafa-fork
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Quick Start

### 1. Training the Model
Train the LSTM network on your CDM JSON data. This processes the data, generates sequences, and optimizes the model.
```bash
python main.py --mode train
```
*The model will be saved to `models/lstm_model.pth`.*

### 2. Running Inference
Generate risk predictions and certainty scores for the dataset.
```bash
python main.py --mode inference
```
*Results will be saved to `results/predictions_lstm.csv`.*

## ⚙️ Configuration

Customize the system behavior in `config.yaml`:

```yaml
data:
  json_path: "data/download.json"  # Path to your CDM data

model:
  type: "LSTM"
  sequence_length: 5               # Number of updates to look back
  hidden_size: 64                  # Size of LSTM hidden layer
  num_layers: 2                    # Number of stacked LSTM layers

training:
  epochs: 50
  learning_rate: 0.01
```

## 🏗️ Project Structure

```
collision-risk-ai/
├── app/
│   ├── pipeline/
│   │   ├── datasource.py       # Data loading (JSON/API)
│   │   └── preprocessor.py     # Sequence generation & grouping
│   ├── model/
│   │   └── lstm_model.py       # PyTorch LSTM architecture
├── data/
│   └── download.json           # Input data
├── models/                     # Saved model artifacts
├── results/                    # Inference output
├── logs/                       # Execution logs
├── config.yaml                 # Configuration
├── main.py                     # Entry point
└── requirements.txt            # Dependencies
```

## 👥 Authors
- Mostafa & Team
