 # -*- coding: utf-8 -*-
"""
Created on 6/29/2020

Author: Joost Berkhout (VU, email: j2.berkhout@vu.nl)

Description: Applies Deep k-nearest neighbors to the triangle and squares data.
"""

import math
import os.path
import shutil

import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.models import load_model
from tensorflow.keras import initializers
import tensorflow.keras

import tools.data_loader
import tools.data_analysis
import settings
from DkNN_utilities import DkNN

np.random.seed(0)

# init
epochs = 10
batch_size = 10
retrain_existing_model = False
k = 15  # number of nearest neighbors to consider per layer

# load data
X, Y = tools.data_loader.load_data()

# training

# Initialize the constructor
model = Sequential()

# Add an input layer
model.add(Dense(units=80,
                kernel_initializer=initializers.RandomNormal(stddev=settings.nrOfPixels**(-.5)),
                input_shape=(settings.nrOfPixels,),
                name='Dense1_80'))

model.add(Activation('relu', name='relu1'))  # for testing: can be replaced by adding activation in previous Dense

# intermediate layer
model.add(Dense(units=40,
                kernel_initializer=initializers.RandomNormal(stddev=settings.nrOfPixels**(-.5)),
                name='Dense2_40'))

model.add(Activation('relu', name='relu2'))  # for testing: can be replaced by adding activation in previous Dense

# Add an output layer
model.add(Dense(units=Y[settings.kinds[0]].shape[-1],
                kernel_initializer=initializers.RandomNormal(stddev=settings.nrOfPixels**(-.5)),
                name='Dense3_3'))

model.add(Activation('softmax', name='softmax'))

model.compile(loss='mean_squared_error',
              optimizer='adam',
              metrics=['accuracy'])

# determine training name of neural net
layer_names = '_'.join([l.name for l in model.layers])
model_name = ('nn_keras_tf2_' + layer_names +
              '_(epochs_{}_batchsize_{})'.format(epochs, batch_size))
model_loc = settings.modelPath + model_name + ".hdf5"

# consider training the model
if os.path.isfile(model_loc) and not retrain_existing_model:
    model = load_model(model_loc)
else:
    print('Start training ' + model_name + '.')

    train_history = model.fit(X['train'],
                              Y['train'],
                              validation_data=(X['valid'], Y['valid']),
                              epochs=epochs,
                              batch_size=batch_size,
                              verbose=1)

    model.save(model_loc)

    # log main_DkNN.py that produced neural net
    script_name = 'main_DkNN'
    nameLogScript = 'log_' + script_name + '_for_' + model_name + '.py'
    try:
        shutil.copyfile(script_name + '.py', settings.modelPath + nameLogScript)
    except FileNotFoundError:
        print('could not save the log, continue without saving.')

# evaluate model on test data
YPred = model.predict(X['test'])
pred_errs = np.average(np.argmax(Y['test'], 1) == np.argmax(YPred, 1))
idxs_falsely_classified = np.argwhere(np.logical_not(np.argmax(Y['test'], 1) == np.argmax(YPred, 1)))[:,0]
print(f'The model accuracy on test data is {pred_errs}')

# get extractor
extractor = tensorflow.keras.Model(inputs=model.inputs,
                                   outputs=model.inputs + [l.output for l in model.layers])
train_features = extractor(X['train'])

# inspect correctly classified image
image_idx = 0
x = X['test'][image_idx:image_idx + 1, :]
y = Y['test'][image_idx:image_idx + 1, :]
test_image_features = extractor(x)
tools.data_analysis.plot_vector_as_image(x, f'label = {y}, output layer1 = {test_image_features[1].numpy()}, output layer3 = {test_image_features[2].numpy()}')
deep_k_NN = DkNN(extractor, X, Y, k, x, y, model.predict(x))
deep_k_NN.plot_NN_layer(1)
deep_k_NN.plot_NN_layer(2)
deep_k_NN.plot_NN_layer(3)
deep_k_NN.plot_NN_layer(4)
deep_k_NN.plot_NN_layer(5)
deep_k_NN.plot_NN_layer(6)

# inspect correctly classified image
image_idx = idxs_falsely_classified[1]
x = X['test'][image_idx:image_idx + 1, :]
y = Y['test'][image_idx:image_idx + 1, :]
test_image_features = extractor(x)
tools.data_analysis.plot_vector_as_image(x, f'label = {y}, output layer1 = {test_image_features[1].numpy()}, output layer3 = {test_image_features[2].numpy()}')
deep_k_NN = DkNN(extractor, X, Y, k, x, y, model.predict(x))
deep_k_NN.plot_NN_layer(1)
deep_k_NN.plot_NN_layer(2)
deep_k_NN.plot_NN_layer(3)
deep_k_NN.plot_NN_layer(4)
deep_k_NN.plot_NN_layer(5)
deep_k_NN.plot_NN_layer(6)

tools.data_analysis.multipage('Results\Figures from Python script main_DkNN.pdf')




# # some specific analysis for TrianglesAndSqaures below
# # ====================================================
#
# # plot datapoints after first label
# fig, ax = plt.subplots()
# train_labels = np.argmax(Y['train'], 1)
# label_symbols = ['s', '^']
# for label_idx in np.unique(train_labels):
#     filter = train_labels == label_idx
#     ax.scatter(train_features[1].numpy()[filter][:, 0],
#                train_features[1].numpy()[filter][:, 1],
#                marker=label_symbols[label_idx],
#                alpha=0.3,
#                label=label_idx)
# ax.legend()
# ax.grid(True)
#
# # inspect weights to first layer
# import mpl_toolkits.axes_grid1 as axes_grid1
# import render
# W1 = model.layers[0].weights[0].numpy()
# B = model.layers[0].weights[1].numpy()
# dim = int(W1.shape[1])
# W11 = W1[:, 0]
# W12 = W1[:, 1]
# W11Im = render.vec2im(W11)
# W12Im = render.vec2im(W12)
#
# # init figure
# fig = plt.figure()
# grid = axes_grid1.AxesGrid(fig,
#                            111,
#                            nrows_ncols=(1, dim),
#                            axes_pad=0.55,
#                            share_all=True,
#                            cbar_location="right",
#                            cbar_mode="each",
#                            cbar_size="5%",
#                            cbar_pad="2%",)
# fig.suptitle('Neural network weights images')
#
# # plot weights
# for i in range(dim):
#     im = grid[i].imshow(render.vec2im(W1[:, i]), cmap='jet')
#     grid[i].set_title('W1{i}'.format(i=i+1) + ' (bias = {})'.format(round(B[i],2)))
#     grid[i].axis('off')
#     grid.cbar_axes[i].colorbar(im)







# # use GradCAM
# # model.summary()
# img = X['test'][0:1,:]
# y_img = np.argmax(Y['test'], 1)[0]
# data = (np.array([img]), y_img)
# #
# from tf_explain.core.grad_cam import GradCAM
# import tf_explain.utils.display
# explainer = GradCAM()
# # Compute GradCAM on VGG16
# grid = explainer.explain(
#     data, model, class_index=1, layer_name='dense_1'
# )
# explainer.save(grid, ".", "grad_cam.png")
#
# import matplotlib.pyplot as plt
# imgplot = plt.imshow(grid.reshape(1,32,32,3)[0])
# tools.data_analysis.plot_vector_as_image(X['train'][0:1,:], f'label = {Y["train"][ 0:1, :]}')
# tools.data_analysis.plot_vector_as_image(grid[0], 'test')
