import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from typing import Sequence
class FaceRecognition(object):
    def __init__(self):
        self.subject_ids = None
        self.faces = None
        self.eigenface_weights = None
        self.mean_image = None
    def eigenfaces(self, train_image_filenames: Sequence[str], subject_ids: Sequence[int]) -> None:
        '''Finds a set of eigenfaces based on the input images.
        The eigenfaces are saved in self.faces and self.eigenface_weights.
        Keyword arguments:
        image_filenames -- A list of image filenames
        subject_ids -- A list of IDs that uniquely identify the subjects
                       in the images
        '''
        # Load images into a list of arrays
        train_images = []
        for filename in train_image_filenames:
            img = Image.open(filename).convert('L') 
            
            # I observed that grayscaling operation is necessary for this to show good accuracy, imageio didn't give good results
            train_images_set = np.array(img).flatten()
            train_images.append(train_images_set)

        # calculate mean average of the images
        train_images = np.array(train_images).T
        mean_image = np.mean(train_images, axis=1)
        # Subtract mean from centred result
        train_images_centered = train_images - mean_image[:, np.newaxis]
        # calculate SVD
        U, S, Vt = np.linalg.svd(train_images_centered, full_matrices=0)
        # U will be Eigenface here
        # calculate eigenface weights, is like a basis to make the new image
        eigenface_weights = U.T @ train_images_centered
        # update the attributes 
        self.subject_ids = subject_ids
        self.faces = U
        self.eigenface_weights = eigenface_weights
        self.mean_image = mean_image
        
    def recognize_faces(self, test_image_filenames: Sequence[str]) -> Sequence[int]:
        '''Finds the eigenfaces that have the highest similarity
        to the input images and returns a list with their indices.
        Keyword arguments:
        image_filenames -- A list of image filenames
        Returns:
        recognised_ids -- A list of ids that correspond to the classifier
                          predictions for the input images
        '''
        # Load test images --> repeat the same process like the previos function

        test_images = []
        for filename in test_image_filenames:
            img = Image.open(filename).convert('L')  # Convert to grayscale
            test_images_set = np.array(img).flatten()
            test_images.append(test_images_set)
        # Subtract mean from centred result
        test_images = np.array(test_images).T
        test_images_centered = test_images - self.mean_image[:, np.newaxis]
        # Project test images onto eigenfaces
        test_weights = self.faces.T @ test_images_centered
        # Find closest training image for each test image
        final_ids = []
        for i in range(test_weights.shape[1]):
            # Compare the weights of train and testing and and summing with numpy to 
            # find the cost/distance within face space having the train and test image coefficients
            cost_value = np.sum(np.square(self.eigenface_weights - test_weights[:, i, np.newaxis]), axis=0)
            best_id = self.subject_ids[np.argmin(cost_value)]
            final_ids.append(best_id)
        return final_ids
