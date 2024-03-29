# import the necessary packages
from collections import OrderedDict
import numpy as np
import cv2
import dlib
import imutils
import os
import csv

facial_features_cordinates = {}

# define a dictionary that maps the indexes of the facial
# landmarks to specific face regions
FACIAL_LANDMARKS_INDEXES = OrderedDict([
    ("Mouth", (48, 68)),
    ("Right_Eyebrow", (17, 22)),
    ("Left_Eyebrow", (22, 27)),
    ("Right_Eye", (36, 42)),
    ("Left_Eye", (42, 48)),
    ("Nose", (27, 35)),
    ("Jaw", (0, 17))
])


def shape_to_numpy_array(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    all_face = np.zeros((68, 2), dtype=dtype)
    mouth_array = np.zeros((20, 2), dtype=dtype)
    eye_array = np.zeros((12, 2), dtype=dtype)
    eyebrow_array = np.zeros((10, 2), dtype=dtype)
    nose_arry = np.zeros((9, 2), dtype=dtype)
    jaw_array = np.zeros((17, 2), dtype=dtype)
    data = {}

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        all_face[i] = (shape.part(i).x, shape.part(i).y)

    jaw_array = all_face[:17, :]
    # jaw_array = np.vstack([jaw_array, [
    #     np.max(jaw_array[:, 0]) - np.min(jaw_array[:, 0]),
    #     np.max(jaw_array[:, 1]) - np.min(jaw_array[:, 1])]])
    eyebrow_array = all_face[17:27, :]
    nose_array = all_face[27:36, :]
    eye_array = all_face[36:48, :]
    mouth_array = all_face[48:, :]
    jaw_list = jaw_array[:, 0].tolist()
    jaw_list.extend(jaw_array[:, 1].tolist())
    nose_list = nose_array[:, 0].tolist()
    nose_list.extend(nose_array[:, 1].tolist())
    eyebrow_list = eyebrow_array[:, 0].tolist()
    eyebrow_list.extend(eyebrow_array[:, 1].tolist())
    eye_list = eye_array[:, 0].tolist()
    eye_list.extend(eye_array[:, 1].tolist())
    mouth_list = mouth_array[:, 0].tolist()
    mouth_list.extend(mouth_array[:,1].tolist())

    data["jaw"] = jaw_list
    data["nose"] = nose_list
    data["eyebrow"] =  eyebrow_list
    data["eye"] = eye_list
    data["mouth"] = mouth_list

    #data["jaw"].append(classify_jaw(jaw_array))
    #data["nose"].append(classify_nose(nose_array))
    #data["eyebrow"].append(classify_eyebrow(eyebrow_array[:, 1]))
    #data["eye"].append(classify_eye(eye_array))
    #data["mouth"].append(classify_mouth(mouth_array))

    # return the list of (x, y)-coordinates
    return data


def visualize_facial_landmarks(image, shape, colors=None, alpha=0.75):
    # create two copies of the input image -- one for the
    # overlay and one for the final output image
    overlay = image.copy()
    output = image.copy()

    # if the colors list is None, initialize it with a unique
    # color for each facial landmark region
    if colors is None:
        colors = [(19, 199, 109), (79, 76, 240), (230, 159, 23),
                  (168, 100, 168), (158, 163, 32),
                  (163, 38, 32), (180, 42, 220)]

    # loop over the facial landmark regions individually
    for (i, name) in enumerate(FACIAL_LANDMARKS_INDEXES.keys()):
        # grab the (x, y)-coordinates associated with the
        # face landmark
        (j, k) = FACIAL_LANDMARKS_INDEXES[name]
        pts = shape[j:k]
        facial_features_cordinates[name] = pts

        # check if are supposed to draw the jawline
        if name == "Jaw":
            # since the jawline is a non-enclosed facial region,
            # just draw lines between the (x, y)-coordinates
            for l in range(1, len(pts)):
                ptA = tuple(pts[l - 1])
                ptB = tuple(pts[l])
                cv2.line(overlay, ptA, ptB, colors[i], 2)

        # otherwise, compute the convex hull of the facial
        # landmark coordinates points and display it
        else:
            hull = cv2.convexHull(pts)
            cv2.drawContours(overlay, [hull], -1, colors[i], -1)

    # apply the transparent overlay
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    # return the output image
    print(facial_features_cordinates)
    return output

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")

ROOT_DIR = os.path.abspath(os.curdir)
image_folder = os.path.join(ROOT_DIR,"images")
jaw = []
nose =[]
eye = []
eyebrow =[]
mouth = []
idx = 0
for img in os.listdir(image_folder):
    print(idx)
    idx+=1
    image_path = os.path.join(image_folder,img)
    # load the input image, resize it, and convert it to grayscale
    image = cv2.imread(image_path)
    image = imutils.resize(image, width=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # detect faceas in the grayscale image
    rects = detector(gray, 1)

    # loop over the face detections
    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the landmark (x, y)-coordinates to a NumPy array
        shape = predictor(gray, rect)

        # dict = {'jaw'     : jaw array,
        #         'nose'    : nose array,
        #         'eyebrow' : eyebrow array,
        #         'eye'     : eye array,
        #         'mouth'   : mouth array
        #         }
        all_face = shape_to_numpy_array(shape)
        all_face["jaw"].insert(0, img)
        all_face["eye"].insert(0, img)
        all_face["mouth"].insert(0, img)
        all_face["eyebrow"].insert(0, img)
        all_face["nose"].insert(0, img)
        jaw.append(all_face["jaw"])
        eye.append(all_face["eye"])
        mouth.append(all_face["mouth"])
        eyebrow.append(all_face["eyebrow"])
        nose.append(all_face["nose"])
        #print(all_face)
        #output = visualize_facial_landmarks(image, shape)
        #cv2.imshow("Image", output)
        #cv2.waitKey(0)


# save data
list = [eyebrow, eye, nose, mouth, jaw]
names = ["eyebrow", "eye", "nose", "mouth", "jaw"]
for i in range(len(list)):
    file_name = names[i]+".csv"
    with open(file_name,'w', encoding='utf8',newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list[i])