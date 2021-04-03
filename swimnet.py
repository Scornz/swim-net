import os
# Stop normal DEBUG from tensorflow (it's annoying)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
# ML/AI
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras.layers.experimental import preprocessing

# Import numpy/pandas
import numpy as np
import pandas as pd

# Plotting packages
import matplotlib.pyplot as plt
import seaborn as sns

import time

# List of all events
events = ("50 FR", "100 FR", "200 FR", "500 FR", "1000 FR", "1650 FR",
          "100 BK", "200 BK", "100 BR", "200 BR", "100 FL", "200 FL",
          "200 IM", "400 IM")

# List of all ages in the data
ages = ("15", "16", "17", "18")

metrics = ("Average Percentage Improved", "Average Power Points")

class SwimNet:

    def __init__(self, data_loc, epochs=120, use_diff = False):
        # Make sure the venv is all set up and running correctly
        print(tf.__version__)
        self.epochs = epochs
        # Load the data set then train the model
        # Send the data location and whether or not to use DIFFERENCES in times
        self.load_dataset(data_loc, use_diff)
        self.train()

    def load_dataset(self, data_location, use_diff):
        raw_dataset = pd.read_csv(data_location, na_values='?', delimiter=',', skipinitialspace=True)
        # Copy the raw-dataset
        # There will be 56 data points (14 events across 4 ages in highschool)
        self.dataset = raw_dataset.copy()

        # If we are to use the DIFFERENCES between time (solely focused on improvement)
        if use_diff:
            self.__process_difference_dataset()

        # Get 85% of all data to train with
        # Set the random state so we get consistent samples
        self.train_dataset = self.dataset.sample(frac=0.9, random_state=12)
        # Drop all indices used in the training dataset
        self.test_dataset = self.dataset.drop(self.train_dataset.index)
        self.train_labels = self.train_dataset.pop('Points')
        self.test_labels = self.test_dataset.pop('Points')
        # Pop the names off of this dataset since this is not necessary to train the NN
        self.train_dataset.pop('Name')
        self.test_dataset.pop('Name')

        # Sums up all ages and averages them for an "average time"
        # This is useful simply to show correlation between speed
        self.event_distribution = pd.DataFrame(columns=events)
        for index, row in self.dataset.iterrows():
            dist = {}
            for e in events:
                # Average over age
                avg = 0
                # Ages swam at
                n = 0
                for a in ages:
                    # Get the time (append event and age)
                    time = row[f'{e} {a}']
                    avg += time
                    # Time might be 0 if it was never swam (or NaN)
                    if time != 0:
                        n += 1
                # If they have never swam this, don't include it
                if (n != 0):
                    dist[e] = (avg / n)

            # Append the dictionary to the dataframe
            self.event_distribution = self.event_distribution.append(
                dist, ignore_index=True)

    def train(self):

        print(f"Starting training for {self.epochs} epochs on {len(self.train_dataset)} data points.")
        start = time.time()
        # Create a normalizing layer
        normalizer = preprocessing.Normalization()
        normalizer.adapt(self.train_dataset)
        # Create the defined model
        model = self.__create_model(normalizer)
        testing_history_callback = TestingHistory(self.test_dataset, self.test_labels)
        # Number of epochs to run (one pass of all training data)
        self.history = model.fit(self.train_dataset, self.train_labels, epochs=self.epochs, validation_split=0.1,
                                 verbose=0, callbacks=[testing_history_callback])

        self.testing_history = testing_history_callback.test_loss

        end = time.time()
        print(f"Training concluded in {round(end - start, 2)} seconds.")

    # Plot and display a graph of the loss over time
    def plot_loss(self):
        # Loss/validation loss
        plt.plot(self.history.history['loss'], label='loss')
        plt.plot(self.history.history['val_loss'], label='val_loss')
        plt.plot(self.testing_history, label='test_loss')
        plt.xlabel('Epoch #')
        plt.ylabel('Error/Loss (mae)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_distribution(self, *args):
        # Plot a pair plot of events (shows correlation of speed, NOT progression)
        sns.pairplot(self.event_distribution[pd.Index(args)], diag_kind='kde')
        plt.show()

    def __create_model(self, normalizer):

        # Simple sequential model (multilayer perceptron)
        model = keras.Sequential()
        model.add(normalizer)
        # Two hidden layers of length 64 (relu is identity for anything above 0)
        model.add(keras.layers.Dense(64, activation='relu'))
        model.add(keras.layers.Dense(64, activation='relu'))
        # Output is one regresssion
        model.add(keras.layers.Dense(1))
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.005)
        # Mean absolute error (mae) is the among the best choices for a regession model here
        # It is the sum of the absolute differences between the labels and the predictions
        model.compile(loss='mean_absolute_error', optimizer=optimizer)
        return model

    def __process_difference_dataset(self):
        for index, row in self.dataset.iterrows():
            dist = {}
            for e in events:
                # previous time
                prev = -1
                for a in ages:
                    # Get the time (append event and age)
                    time = row[f'{e} {a}']
                    if time == 0:
                        continue

                    # The first recorded time will have an improvement of "zero"
                    # This could maybe be modified, not sure what would go well here other than that
                    if prev == -1:
                        prev = time
                        row[f'{e} {a}'] = 0
                    
                    # Subtract the time (so negative means drop, positive means added)
                    self.dataset.loc[index, [f'{e} {a}']] = time - prev
                    prev = time


# Callback function that allows for the testing dataset to be run after each epoch
# This is the BEST measurement of performance (since validation set influences hyperparameters)
class TestingHistory(keras.callbacks.Callback):

    # Will be initialized with the testing set
    def __init__(self, test_dataset, test_labels):
        super(TestingHistory, self).__init__()
        self.test_dataset = test_dataset
        self.test_labels = test_labels

    # Initialize the history
    def on_train_begin(self, logs={}):
        self.test_loss = []

    # Run an evaluate after every epoch to get mae
    def on_epoch_end(self, epoch, logs=None):
        loss = self.model.evaluate(
            self.test_dataset, self.test_labels, verbose=0)
        self.test_loss.append(loss)
