import torch
import torch.nn as nn
import torch.nn.functional as F
from litert_torch import convert


class CellCNN(nn.Module):
    def __init__(self):
        super().__init__()

        # Feature extractor simplificado
        self.conv1 = nn.Conv2d(1, 8, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(16)

        self.pool = nn.MaxPool2d(2, 2)

        # Classifier direto
        self.fc = nn.Linear(16 * 7 * 7, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))

        x = torch.flatten(x, 1)
        x = self.fc(x)

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

        print("Modelo convertido com sucesso!")



if __name__ == "__main__":
    CellCNN.convert_to_tflite()
