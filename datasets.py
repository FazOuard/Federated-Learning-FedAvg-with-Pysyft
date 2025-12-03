# datasets.py

import torch
from torch.utils.data import random_split
from torchvision import datasets, transforms
from typing import Optional, Tuple
import numpy as np

MNIST_ROOT = "./tmp/mnist_data"

MNIST_PART_1 = "MNIST Part 1"
MNIST_PART_2 = "MNIST Part 2"

DATASETS = {
    MNIST_PART_1: 0,
    MNIST_PART_2: 1,
}

NAMES = tuple(DATASETS.keys())


def _load_full_mnist(root: str = MNIST_ROOT) -> datasets.MNIST:
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    return datasets.MNIST(root=root, train=True, download=True, transform=transform)


def _get_two_splits_tensors() -> Tuple[Tuple[torch.Tensor, torch.Tensor],
                                       Tuple[torch.Tensor, torch.Tensor]]:
    full = _load_full_mnist()
    n = len(full)
    n1 = n // 2
    n2 = n - n1
    ds1, ds2 = random_split(full, [n1, n2])

    def to_tensors(subset):
        xs, ys = [], []
        for img, label in subset:
            xs.append(img)                 # img: [1,28,28]
            ys.append(label)
        X = torch.stack(xs)               # [N,1,28,28]
        y = torch.tensor(ys, dtype=torch.long)
        return X, y

    return to_tensors(ds1), to_tensors(ds2)


def load_data(name: str) -> Optional[Tuple[torch.Tensor, torch.Tensor]]:
    if name not in DATASETS:
        print(f"Name of Datasite {name} is invalid, or incorrect. Please check!")
        return None
    (X1, y1), (X2, y2) = _get_two_splits_tensors()
    return (X1, y1) if DATASETS[name] == 0 else (X2, y2)


def generate_mock(data: Tuple[torch.Tensor, torch.Tensor],
                  seed: int = 12345) -> Tuple[torch.Tensor, torch.Tensor]:
    X, y = data
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), size=len(X), replace=True)
    return X[idx], y[idx]
