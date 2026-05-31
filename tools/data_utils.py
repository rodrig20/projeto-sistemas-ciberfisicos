import os
import numpy as np
from PIL import Image
from torchvision import datasets, transforms
from torch.utils.data import Subset, DataLoader


# -----------------------
# EMPTY DATA REALISTA
# -----------------------
def generate_empty_images(save_dir, num_images, img_size=28):
    os.makedirs(save_dir, exist_ok=True)

    for i in range(num_images):

        img = np.zeros((img_size, img_size), dtype=np.float32)

        noise = np.random.uniform(0, 0.08, (img_size, img_size))
        illumination = np.random.uniform(0, 0.05)

        img = img + noise + illumination
        img = np.clip(img, 0, 1)

        img = (img * 255).astype(np.uint8)

        Image.fromarray(img, mode="L").save(
            os.path.join(save_dir, f"empty_{i}.png")
        )


# -----------------------
# DATA PREP
# -----------------------
def prepare_data(data_root="data"):

    cross_dir = os.path.join(data_root, "cross")
    round_dir = os.path.join(data_root, "round")
    empty_dir = os.path.join(data_root, "empty")

    cross_count = len(os.listdir(cross_dir))
    round_count = len(os.listdir(round_dir))
    target_empty = max(cross_count, round_count)

    if not os.path.exists(empty_dir) or len(os.listdir(empty_dir)) == 0:
        print("A gerar empty dataset...")
        generate_empty_images(empty_dir, target_empty)

    # 🔥 FORÇAR GRAYSCALE REAL (CRÍTICO)
    transform = transforms.Compose([
        transforms.Lambda(lambda img: img.convert("L")),  # força 1 canal
        transforms.Resize((28, 28)),
        transforms.RandomRotation(10),
        transforms.RandomAffine(
            degrees=0,
            translate=(0.1, 0.1),
            scale=(0.7, 1)
        ),
        transforms.ToTensor()
    ])

    dataset = datasets.ImageFolder(
        root=data_root,
        transform=transform
    )

    targets = np.array(dataset.targets)

    train_idx, test_idx = [], []

    for cls in np.unique(targets):
        idx = np.where(targets == cls)[0]
        np.random.shuffle(idx)

        split = int(0.8 * len(idx))

        train_idx.extend(idx[:split])
        test_idx.extend(idx[split:])

    train_dataset = Subset(dataset, train_idx)
    test_dataset = Subset(dataset, test_idx)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    return train_loader, test_loader