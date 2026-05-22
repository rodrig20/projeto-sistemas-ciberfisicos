import os
import numpy as np
import tensorflow as tf
from PIL import Image


# -----------------------------
# CARREGAR MODELO
# -----------------------------
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("\n=== MODEL INFO ===")
print("INPUT:", input_details)
print("OUTPUT:", output_details)


# -----------------------------
# MAPEAMENTO DE CLASSES
# -----------------------------
class_map = {
    "cross": 0,
    "empty": 1,
    "round": 2
}

inv_class_map = {v: k for k, v in class_map.items()}


# -----------------------------
# PREPROCESSAMENTO
# -----------------------------
def load_image(path):
    img = Image.open(path).convert("L")
    img = img.resize((28, 28))
    img = np.array(img).astype(np.float32) / 255.0
    
    # Binarização
    img = (img > 0.5).astype(np.float32)
    
    img = img.reshape(1, 1, 28, 28)
    return img


# -----------------------------
# INFERÊNCIA
# -----------------------------
def predict(img):
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]["index"])
    return output


# -----------------------------
# TESTE DATASET
# -----------------------------
def test_folder(folder, label):
    correct = 0
    total = 0

    for file in os.listdir(folder):
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        path = os.path.join(folder, file)

        img = load_image(path)
        output = predict(img)

        pred = np.argmax(output)

        if pred == label:
            correct += 1

        total += 1

    acc = 100 * correct / total if total > 0 else 0

    print(f"{folder} -> Accuracy: {acc:.2f}% ({correct}/{total})")

    return correct, total


# -----------------------------
# MAIN TEST
# -----------------------------
if __name__ == "__main__":

    print("\n=== TESTE POR CLASSE ===")

    total_correct = 0
    total_samples = 0

    for cls_name, cls_id in class_map.items():

        folder = os.path.join("data", cls_name)

        correct, total = test_folder(folder, cls_id)

        total_correct += correct
        total_samples += total

    overall_acc = 100 * total_correct / total_samples

    print("\n=======================")
    print(f"OVERALL ACCURACY: {overall_acc:.2f}%")
    print("=======================\n")