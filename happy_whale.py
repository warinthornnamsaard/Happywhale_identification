# -*- coding: utf-8 -*-
"""Happy_whale.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M_cjsa56MOPkGMypKjPP8kXuOAjbrR_J
"""

!pip install kaggle

!mkdir ~/.kaggle

!cp kaggle.json ~/.kaggle/

!chmod 600 ~/.kaggle/kaggle.json

!kaggle competitions download -c happy-whale-and-dolphin

!unzip happy-whale-and-dolphin.zip

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import shutil
import os
import tensorflow as tf

from keras.layers import Input, Lambda, Dense 
from keras.models import Model
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras import layers , models
from tensorflow.keras.utils import to_categorical             ## encode numbers to one-hot encode form
from tensorflow.keras.callbacks import ModelCheckpoint
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder                ## encode string labels to numbers

species = pd.read_csv("/content/train.csv")

os.mkdir("happywhalesortbyspecies")

species_folder = set(species['species'])
parent_dir = './happywhalesortbyspecies/'
for New_folder in species_folder:
  path = os.path.join(parent_dir,New_folder)
  os.mkdir(path)

numpy_species = np.array(species)
sources = "./train_images"
des = "./happywhalesortbyspecies"
for filename in numpy_species:
  target = sources+"/"+filename[0]
  destination = des+"/"+filename[1]
  shutil.move(target, destination)

generator = ImageDataGenerator(
    rescale = 1. /255,
    horizontal_flip = True,
    validation_split=0.2)

train_generator = generator.flow_from_directory(
    directory=r"./happywhalesortbyspecies/",
    target_size=(224, 224),
    color_mode="rgb",
    batch_size=32,
    class_mode="categorical",
    shuffle=True,
    seed=42,
    subset='training'
)

valid_generator = generator.flow_from_directory(
    directory=r"./happywhalesortbyspecies/",
    target_size=(224, 224),
    color_mode="rgb",
    batch_size=32,
    class_mode="categorical",
    shuffle=True,
    seed=42,
    subset='validation'
)

from tensorflow.keras.applications import ResNet152V2

pretrained_model = tf.keras.applications.ResNet152V2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg')

pretrained_model.trainable = False

inputs = pretrained_model.input

outputs = layers.Dense(30, activation='softmax')(pretrained_model.output)

model = models.Model(inputs, outputs)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

check_point1 = ModelCheckpoint(
    filepath= 'ResnetV2-{epoch:03d}-{val_loss:03f}.h5',                ## model check-point file 
    save_weights_only=False,
    monitor='val_loss',
    mode='min',
    save_best_only=True)

STEP_SIZE_TRAIN=train_generator.n//train_generator.batch_size
STEP_SIZE_VALID=valid_generator.n//valid_generator.batch_size
history = model.fit_generator(generator=train_generator,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    validation_data=valid_generator,
                    validation_steps=STEP_SIZE_VALID,
                    epochs=5,
                    callbacks=[check_point1]
)