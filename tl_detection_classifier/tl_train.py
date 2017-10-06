from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tl_train_helper import *
from augmentation import *

import keras
from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Cropping2D, Dropout
from keras.layers.convolutional import Conv2D
from keras.layers.pooling import MaxPooling2D

# Load dataset to train and validate on as pandas DataFrame
samples_df = import_data(source='simulator/')

# Balance the dataset
samples_df_bal = balance_dataset(samples_df)

# Get np.arrays with sampels
samples = get_dataset(samples_df_bal)

# Split into train and test set
train_samples, val_samples = train_test_split(samples, test_size=.3)
print("# Split Training / Validation")
print("# - Training size: {}".format(len(train_samples)))
print("# - Validation size: {}".format(len(val_samples)))

# Set up generators
train_generator = generator(train_samples, batch_size=32)
val_generator = generator(val_samples, batch_size=32)

#
#  Model
#

model = Sequential([
    # Normalize
    Lambda(lambda x: (x / 255.0) - 0.5, input_shape=(600, 800, 3)),

    # Convolutional Layers
    Conv2D(6, 5, 5, activation='relu'),
    MaxPooling2D(),
    Conv2D(16, 5, 5, activation='relu'),
    MaxPooling2D(),
    Dropout(0.5),

    # Fully connected layers
    Flatten(),
    Dense(500, activation='relu'),
    Dropout(0.5),
    Dense(180, activation='relu'),
    Dense(84, activation='relu'),
    Dense(4)])

model.compile(loss='mse', optimizer='adam')

hist = model.fit_generator(train_generator,
                           samples_per_epoch=len(train_samples) * 2,
                           validation_data=val_generator,
                           nb_val_samples=len(val_samples) * 2,
                           nb_epoch=2)

# Save the model
model.save('../model.h5')

# Plot and history
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
plt.show()
plt.savefig('history.png')
