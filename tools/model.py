import torch
import torch.nn as nn
import torch.nn.functional as F

from litert_torch import convert


import torch
import torch.nn as nn
import torch.nn.functional as F


class CellCNN(nn.Module):
    def __init__(self):
        super().__init__()

        # feature extractor leve mas sólido
        self.conv1 = nn.Conv2d(1, 8, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(2, 2)

        self.gap = nn.AdaptiveAvgPool2d((1, 1))

        # classifier
        self.fc1 = nn.Linear(16, 12)
        self.fc2 = nn.Linear(12, 3)

    def forward(self, x):

        x = self.pool(F.relu(self.conv1(x)))  # 28 → 14
        x = self.pool(F.relu(self.conv2(x)))  # 14 → 7

        x = self.gap(x)

        x = torch.flatten(x, 1)

        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return x

    @staticmethod
    def convert_to_tflite(
        model_path="model.pth",
        output_path="model.tflite",
    ):
        model = CellCNN()

        model.load_state_dict(
            torch.load(
                model_path,
                map_location="cpu",
            )
        )

        model.eval()

        edge_model = convert(
            model,
            sample_args=(
                torch.randn(1, 1, 28, 28),
            ),
        )

        edge_model.export(output_path)

        print("Modelo convertido!")



if __name__ == "__main__":
    CellCNN.convert_to_tflite()
