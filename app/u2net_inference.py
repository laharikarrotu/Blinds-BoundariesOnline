import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2
import os

from .u2net import U2NETP  # Use the small model

MODEL_PATH = os.path.join('models', 'u2netp.pth')

class U2NetWindowDetector:
    def __init__(self, model_path=MODEL_PATH):
        self.model = U2NETP(3, 1)
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()

    def preprocess(self, image_path):
        image = Image.open(image_path).convert('RGB')
        image = image.resize((320, 320))
        img_np = np.array(image) / 255.0
        img_np = img_np.transpose((2, 0, 1))
        img_tensor = torch.from_numpy(img_np).unsqueeze(0).float()
        return img_tensor, image

    def postprocess(self, pred, save_path):
        pred = pred.squeeze().cpu().data.numpy()
        pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
        pred = (pred * 255).astype(np.uint8)
        mask = Image.fromarray(pred)
        mask = mask.resize((320, 320))
        mask.save(save_path)
        return save_path

    def detect_window(self, image_path, mask_save_path):
        img_tensor, _ = self.preprocess(image_path)
        with torch.no_grad():
            d1, *_ = self.model(img_tensor)
            pred = d1[:, 0, :, :]
        return self.postprocess(pred, mask_save_path) 