#from matplotlib.animation import FuncAnimation
from ultralytics import YOLO
import cv2
import torch
import numpy as np
from time import time
from PIL import Image
import os
#import matplotlib.pyplot as plt
import time


class ObjectDetection:

      def __init__(self, data, epochs, patience = 10, pretrained = 'yolov11x.pt'):
            self.data = data
            self.epochs = epochs
            self.patience = patience

            if torch.cuda.is_available():
                  self.device = 'cuda'  # NVIDIA GPU
            else:
                  self.device = 'cpu'  # Fallback to CPU
                  
            print('Device: ', self.device)

            self.model = self.load_model(pretrained)

      def load_model(self, pretrained='yolov11x.pt'):
            model = YOLO(pretrained) #pretrained model  
            model.fuse() # opimising performance, reducing complexity, imporve inference speed
            return model
      
      def load_custom_model(self, num=None, path=None):
            if path is not None:
                  model = YOLO(path)
                  self.model = model
            else:
                  model =  YOLO(f'./runs/detect/train{num}/weights/best.pt')
                  self.model = model
      
      def train_model(self, augment=False):
            results= self.model.train(data=self.data, epochs = self.epochs, patience=self.patience, batch=8, imgsz=int(1920), augment=augment)
            return results
