import torch
import torch.nn as nn
import torch.optim as optim

from model import CellCNN
from data_utils import prepare_data


def train():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_loader, test_loader = prepare_data()

    model = CellCNN().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # -----------------------
    # TRAIN LOOP
    # -----------------------
    num_epochs = 10

    for epoch in range(num_epochs):

        model.train()
        total_loss = 0

        for data, target in train_loader:

            data, target = data.to(device), target.to(device)
            
            # Binarização: converte pixels > 0.5 para 1.0, caso contrário 0.0
            data = (data > 0.5).float()

            optimizer.zero_grad()

            output = model(data)

            loss = criterion(output, target)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{num_epochs} | Loss: {total_loss:.4f}")

    # -----------------------
    # EVAL
    # -----------------------
    model.eval()

    correct, total = 0, 0

    with torch.no_grad():
        for data, target in test_loader:

            data, target = data.to(device), target.to(device)

            output = model(data)

            _, predicted = torch.max(output, 1)

            total += target.size(0)
            correct += (predicted == target).sum().item()

    print(f"\nAccuracy: {100 * correct / total:.2f}%")

    torch.save(model.state_dict(), "model.pth")

if __name__ == "__main__":
    train()