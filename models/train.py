from keras.callbacks import CSVLogger, ModelCheckpoint, EarlyStopping
from keras.callbacks import ReduceLROnPlateau
from keras.preprocessing.image import ImageDataGenerator

from cnn import mini_XCEPTION
import numpy as np
import h5py
import sklearn
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split


def uint2float(x):
    x = x.astype('float32')
    x = x / 255.0
    x = x - 0.5
    x = x * 2.0
    return x


# parameters

batch_size = 32
num_epochs = 10000
input_shape = (48, 48, 1)
validation_split = 0.1
num_classes = 7
patience = 50
base_path = 'models/test/'

# data generator
data_generator = ImageDataGenerator(featurewise_center=False,
                                    featurewise_std_normalization=False,
                                    rotation_range=10,
                                    width_shift_range=0.1,
                                    height_shift_range=0.1,
                                    zoom_range=.1,
                                    horizontal_flip=True)

# model parameters/compilation
model = mini_XCEPTION(input_shape, num_classes)
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

datasets = ['fer2013']

for dataset_name in datasets:
    print('Training dataset:', dataset_name)
    # callbacks
    log_file_path = base_path + dataset_name + '_emotion_training.log'
    csv_logger = CSVLogger(log_file_path, append=False)
    early_stop = EarlyStopping('val_loss', patience=patience)
    reduce_lr = ReduceLROnPlateau('val_loss',
                                  factor=0.1,
                                  patience=int(patience / 4),
                                  verbose=1)
    trained_models_path = base_path + dataset_name + '_mini_XCEPTION'
    model_names = trained_models_path + '.{epoch:02d}-{accuracy:.2f}.hdf5'
    model_checkpoint = ModelCheckpoint(model_names,
                                       'val_loss',
                                       verbose=1,
                                       save_best_only=True)
    callbacks = [model_checkpoint, csv_logger, early_stop, reduce_lr]

    # loading dataset
    f = h5py.File('models/Data.hdf5', 'r')
    X = f['X'][()]  # type: ignore
    X = uint2float(X)
    Y = f['Y'][()]  # type: ignore
    f.close()
    #X = np.load('X.npy')
    #Y = np.load('Y.npy')
    train_X, test_X, train_Y, test_Y = train_test_split(
        X, Y, test_size=validation_split, random_state=0)

    model.fit_generator(data_generator.flow(train_X, train_Y, batch_size),
                        steps_per_epoch=len(train_X) / batch_size,
                        epochs=num_epochs,
                        verbose=1,
                        callbacks=callbacks,
                        validation_data=(test_X, test_Y))
