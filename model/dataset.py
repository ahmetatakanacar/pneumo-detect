import os
from collections import Counter
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
from torchvision import datasets, transforms
import config

train_transform = transforms.Compose([
    transforms.Resize((config.IMG_SIZE, config.IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
])

eval_transform = transforms.Compose([
    transforms.Resize((config.IMG_SIZE, config.IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD),
])

def get_dataloaders():

    train_dir = os.path.join(config.DATA_DIR, "train")
    test_dir = os.path.join(config.DATA_DIR, "test")

    base = datasets.ImageFolder(train_dir)
    targets = [label for _, label in base.samples]

    train_idx, val_idx = train_test_split(
        np.arange(len(targets)),
        test_size=config.VAL_SPLIT,
        stratify=targets,
        random_state=config.SEED,
    )

    train_full = datasets.ImageFolder(train_dir, transform=train_transform)
    val_full = datasets.ImageFolder(train_dir, transform=eval_transform)

    train_dataset = Subset(train_full, train_idx)
    val_dataset = Subset(val_full, val_idx)
    test_dataset = datasets.ImageFolder(test_dir, transform=eval_transform)

    train_targets = [targets[i] for i in train_idx]
    class_counts = Counter(train_targets)
    class_weights = {cls: 1.0 / count for cls, count in class_counts.items()}
    sample_weights = [class_weights[t] for t in train_targets]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, sampler=sampler,
                               num_workers=config.NUM_WORKERS)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False,
                             num_workers=config.NUM_WORKERS)
    test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False,
                              num_workers=config.NUM_WORKERS)

    class_names = base.classes
    return train_loader, val_loader, test_loader, class_names