import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "chest_xray")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "checkpoints")
BEST_MODEL_PATH = os.path.join(CHECKPOINT_DIR, "best_model.pth")

IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
VAL_SPLIT = 0.2
SEED = 42

BATCH_SIZE = 32
NUM_WORKERS = 4
HEAD_EPOCHS = 6
HEAD_LR = 0.001
FINETUNE_EPOCHS = 10
FINETUNE_LR = 0.001

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

os.makedirs(CHECKPOINT_DIR, exist_ok=True)