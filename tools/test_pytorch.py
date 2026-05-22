import torch
from model import CellCNN
from data_utils import prepare_data
import numpy as np

def test_pytorch_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _, test_loader = prepare_data()
    
    model = CellCNN().to(device)
    model.load_state_dict(torch.load("model.pth", map_location=device))
    model.eval()
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            
            # Binarização
            data = (data > 0.5).float()
            
            output = model(data)
            _, predicted = torch.max(output, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            
    print(f"PyTorch Model Accuracy: {100 * correct / total:.2f}%")

if __name__ == "__main__":
    test_pytorch_model()
