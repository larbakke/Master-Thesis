print("Importing libraries...")

from model import ObjectDetection
print("Libraries imported.")

def main():
      print("Training model...")
      swimmer_data="../datasetAvalanche.yaml"
      epochs = 1
      patience = 1
      
      swimmerDetection = ObjectDetection(swimmer_data, epochs, patience, pretrained='yolo11x.pt')
      swimmerDetection.train_model(augment=True)

if __name__ == '__main__':
      main()
