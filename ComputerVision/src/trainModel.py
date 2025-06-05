print("Importing libraries...")

from model import ObjectDetection
print("Libraries imported.")

def main():
      print("Training model...")
      swimmer_data="./datasetAvalanche.yaml"
      epochs = 1000
      patience = 15
      
      swimmerDetection = ObjectDetection(swimmer_data, epochs, patience, pretrained='yolo11x.pt')
      swimmerDetection.train_model(augment=True)

if __name__ == '__main__':
      main()
