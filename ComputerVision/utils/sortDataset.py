import os
import random
import shutil

def create_directories(base_dir, categories):
    for category in categories:
        os.makedirs(os.path.join(base_dir, category), exist_ok=True)

def move_files(file_pairs, image_dest, label_dest):
    for img_file, label_file in file_pairs:
        shutil.move(img_file, image_dest)
        shutil.move(label_file, label_dest)

def split_data(file_pairs, train_pct, val_pct):
    random.shuffle(file_pairs)
    total_files = len(file_pairs)
    train_end = int(train_pct * total_files)
    val_end = train_end + int(val_pct * total_files)
    
    train_files = file_pairs[:train_end]
    val_files = file_pairs[train_end:val_end]
    test_files = file_pairs[val_end:]
    
    return train_files, val_files, test_files

def sort_files(labels_dir, images_dir, dest_dir, train_pct=0.7, val_pct=0.2, test_pct=None):
    if test_pct is None:
        test_pct = 1.0 - train_pct - val_pct
    
    # Check if the total of percentages is 1.0
    if not round(train_pct + val_pct + test_pct, 3) == 1.0:
        raise ValueError(f"The sum of train_pct, val_pct, and test_pct must be 1.0, but it equals {round(train_pct + val_pct + test_pct, 3)}")

    # Create the required directories
    print('Creating directories...')
    create_directories(os.path.join(dest_dir, 'images'), ['train', 'val', 'test'])
    create_directories(os.path.join(dest_dir, 'labels'), ['train', 'val', 'test'])

    # Get lists of label and image files, ensuring each image has a corresponding label
    label_files = [os.path.join(labels_dir, f) for f in os.listdir(labels_dir) if f.endswith('.txt')]
    image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    # Match images with labels by base filename
    base_names = {os.path.splitext(os.path.basename(f))[0] for f in label_files} & \
                 {os.path.splitext(os.path.basename(f))[0] for f in image_files}
    file_pairs = [(os.path.join(images_dir, f"{name}.jpg"), os.path.join(labels_dir, f"{name}.txt")) for name in base_names]
    
    # Split the data into train, val, and test sets
    train_files, val_files, test_files = split_data(file_pairs, train_pct, val_pct)
    
    # Move files into their respective directories
    print('Moving files...')
    move_files(train_files, os.path.join(dest_dir, 'images', 'train'), os.path.join(dest_dir, 'labels', 'train'))
    print('Moved train files.')
    move_files(val_files, os.path.join(dest_dir, 'images', 'val'), os.path.join(dest_dir, 'labels', 'val'))
    print('Moved val files.')
    move_files(test_files, os.path.join(dest_dir, 'images', 'test'), os.path.join(dest_dir, 'labels', 'test'))
    print('Moved test files.')

if __name__ == "__main__":
    labels_directory = 'rawData/allLabels'
    images_directory = 'rawData/allImages'
    destination_directory = 'data/avalanceDataset1.0'
    
    print('Sorting files...')
    sort_files(labels_directory, images_directory, destination_directory, train_pct=0.7, val_pct=0.2)
    print('Files sorted successfully.')
