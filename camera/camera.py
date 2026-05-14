import gc
import time
import image
import sensor
import ml



class BoardBlobDetector:
    def __init__(self):
        sensor.reset()
        sensor.set_pixformat(sensor.GRAYSCALE)
        sensor.set_framesize(sensor.B128X128)
        sensor.set_auto_exposure(False)
        sensor.skip_frames(time=2000)

        self.clock = time.clock()

        self.threshold = (80, 255)

        self.board_roi = (20, 20, 88, 88)

        gc.collect()

        try:
            self.model = ml.Model(
                "model.tflite",
                load_to_fb=True,
                always_console_output=False,
            )

        except Exception as e:

            print("Error2:", e)
            exit(1)

        gc.collect()

    def preprocess_cell(self, cell_img):
        cell_img.invert()
        cell_img.erode(1)
        cell_img.dilate(1)

        w = cell_img.width()
        h = cell_img.height()

        cropped = cell_img.copy(
            roi=(2, 2, w - 4, h - 4)
        )

        resized = image.Image(28, 28, sensor.GRAYSCALE)

        resized.draw_image(
            cropped,
            0, 0,
            x_scale=28 / cropped.width(),
            y_scale=28 / cropped.height()
        )

        arr = resized.to_ndarray("f")
        arr = arr.reshape((1, 1, 28, 28))
        arr=arr/255.0

        #print("image:", arr[0][0])
        pred = self.model.predict([arr])
        out = pred[0][0]

        best_idx = 0
        best_val = out[0]

        for i in range(1, len(out)):
            if out[i] > best_val:
                best_val = out[i]
                best_idx = i

        return best_idx

    def extract_grid(self, board_img):

        w_board = board_img.width()
        h_board = board_img.height()

        cell_w = w_board // 3
        cell_h = h_board // 3

        predictions = []

        for row in range(3):
            for col in range(3):

                cx = col * cell_w
                cy = row * cell_h

                cell = board_img.copy(
                    roi=(cx, cy, cell_w, cell_h)
                )

                out = self.preprocess_cell(cell)

                predictions.append(out)

                del cell

            gc.collect()

        return predictions

    def scan(self):

        self.clock.tick()

        img = sensor.snapshot()
        img.gaussian(1)

        # bounding box do tabuleiro
        x, y, w, h = self.board_roi
        img.draw_rectangle(
            self.board_roi,
            color=255,
            thickness=2,
        )

        # crop do tabuleiro
        board_img = img.copy(roi=(x, y, w, h))

        cell_w = w // 3
        cell_h = h // 3

        results = []

        for row in range(3):
            for col in range(3):

                cx = x + col * cell_w
                cy = y + row * cell_h

                # desenhar cada célula no frame original
                img.draw_rectangle(
                    (cx, cy, cell_w, cell_h),
                    color=200,
                    thickness=1
                )

        # agora inferência separada (como já tinhas)
        results = self.extract_grid(board_img)

        fps = self.clock.fps()

        return results, fps


scanner = BoardBlobDetector()

while True:
    try:
        results, fps = scanner.scan()
        print(
            "FPS:", fps,
            "Predictions:",
            results
        )
    except Exception as e:
        print("Erro1:", e)
        gc.collect()

    time.sleep_ms(100)
