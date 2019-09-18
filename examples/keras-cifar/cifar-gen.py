from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import numpy as np
import os
import wandb
from wandb.keras import WandbCallback
import tensorflow as tf

run = wandb.init()
config = run.config
config.dropout = 0.25
config.dense_layer_nodes = 100
config.learn_rate = 0.08
config.batch_size = 128
config.epochs = 10

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
num_classes = len(class_names)

(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# Convert class vectors to binary class matrices.
y_train = tf.keras.utils.to_categorical(y_train, num_classes)
y_test = tf.keras.utils.to_categorical(y_test, num_classes)

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Conv2D(32, (3, 3), padding='same',
                                 input_shape=X_train.shape[1:], activation='relu'))
model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
model.add(tf.keras.layers.Dropout(config.dropout))

model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(config.dense_layer_nodes, activation='relu'))
model.add(tf.keras.layers.Dropout(config.dropout))
model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer="adam",
              metrics=['accuracy'])
# log the number of total parameters
config.total_params = model.count_params()
print("Total params: ", config.total_params)
X_train = X_train.astype('float32') / 255.
X_test = X_test.astype('float32') / 255.

datagen = ImageDataGenerator(width_shift_range=0.1)
datagen.fit(X_train)


# Fit the model on the batches generated by datagen.flow().
model.fit_generator(datagen.flow(X_train, y_train,
                                 batch_size=config.batch_size),
                    steps_per_epoch=X_train.shape[0] // config.batch_size,
                    epochs=config.epochs,
                    validation_data=(X_test, y_test),
                    callbacks=[WandbCallback(data_type="image", labels=class_names)])