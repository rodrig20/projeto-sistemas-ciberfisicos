import torch
from PIL import Image
from tools.model import CellCNN
from tools.data_utils import prepare_data

def predict_image(img_path, model_path="model.pth"):
    _, _, transform = prepare_data()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = CellCNN().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    img = Image.open(img_path)
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img)
        pred = torch.argmax(output, dim=1)

    classes = ["empty", "cross", "round"]
    return classes[pred.item()]
