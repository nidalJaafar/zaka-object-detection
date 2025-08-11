import io

from PIL import Image
from ultralytics import YOLO


class Model:
    def __init__(self):
        self.model = YOLO('./model/model.pt')

    def predict(self, file):
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        annotated_img = self.model.predict(
            source=img,
            save=False
        )[0].plot()
        annotated_img_rgb = annotated_img[:, :, ::-1]
        img_pil = Image.fromarray(annotated_img_rgb)
        img_io = io.BytesIO()
        img_pil.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        return img_io
