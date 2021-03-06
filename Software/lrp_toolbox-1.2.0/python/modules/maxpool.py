'''
@author: Sebastian Lapuschkin
@author: Gregoire Montavon
@maintainer: Sebastian Lapuschkin
@contact: sebastian.lapuschkin@hhi.fraunhofer.de
@date: 14.08.2015
@version: 1.2+
@copyright: Copyright (c)  2015, Sebastian Lapuschkin, Alexander Binder, Gregoire Montavon, Klaus-Robert Mueller
@license : BSD-2-Clause
'''

import numpy as np
from module import Module

# -------------------------------
# Max Pooling layer
# -------------------------------

class MaxPool(Module):
    def __init__(self,pool=(2,2),stride=(2,2)):
        '''
        Constructor for the max pooling layer object

        Parameters
        ----------

        pool : tuple (h,w)
            the size of the pooling mask in vertical (h) and horizontal (w) direction

        stride : tuple (h,w)
            the vertical (h) and horizontal (w) step sizes between filter applications.
        '''

        Module.__init__(self)

        self.pool = pool
        self.stride = stride


    def forward(self,X):
        '''
        Realizes the forward pass of an input through the max pooling layer.

        Parameters
        ----------
        X : numpy.ndarray
            a network input, shaped (N,H,W,D), with
            N = batch size
            H, W, D = input size in heigth, width, depth

        Returns
        -------
        Y : numpy.ndarray
            the max-pooled outputs, reduced in size due to given stride and pooling size
        '''

        self.X = X
        N,H,W,D = X.shape

        hpool,   wpool   = self.pool
        hstride, wstride = self.stride

        #assume the given pooling and stride parameters are carefully chosen.
        Hout = int((H - hpool) / hstride + 1)
        Wout = int((W - wpool) / wstride + 1)

        #initialize pooled output
        self.Y = np.zeros((N,Hout,Wout,D))

        for i in range(Hout):
            for j in range(Wout):
                self.Y[:,i,j,:] = X[:, i*hstride:i*hstride+hpool: , j*wstride:j*wstride+wpool: , : ].max(axis=(1,2))
        return self.Y


    def backward(self,DY):
        '''
        Backward-passes an input error gradient DY towards the domintly ativating neurons of this max pooling layer.

        Parameters
        ----------

        DY : numpy.ndarray
            an error gradient shaped same as the output array of forward, i.e. (N,Hy,Wy,Dy) with
            N = number of samples in the batch
            Hy = heigth of the output
            Wy = width of the output
            Dy = output depth = input depth


        Returns
        -------

        DX : numpy.ndarray
            the error gradient propagated towards the input

        '''

        N,H,W,D = self.X.shape

        hpool,   wpool   = self.pool
        hstride, wstride = self.stride

        #assume the given pooling and stride parameters are carefully chosen.
        Hout = int((H - hpool) / hstride + 1)
        Wout = int((W - wpool) / wstride + 1)

        #distribute the gradient towards the max activation(s)
        #the max activation value is already known via self.Y
        DX = np.zeros_like(self.X,dtype=np.float)
        for i in range(int(Hout)):
            for j in range(int(Wout)):
                DX[:,i*hstride:i*hstride+hpool , j*wstride:j*wstride+wpool,:] += DY[:,i:i+1,j:j+1,:] * (self.Y[:,i:i+1,j:j+1,:] == self.X[:, i*hstride:i*hstride+hpool , j*wstride:j*wstride+wpool , : ])
        return DX


    def clean(self):
        self.X = None
        self.Y = None


    def lrp(self,R, lrp_var=None,param=1.):
        '''
        performs LRP by calling subroutines, depending on lrp_var and param

        Parameters
        ----------

        R : numpy.ndarray
            relevance input for LRP.
            should be of the same shape as the previously produced output by Maxpool.forward

        lrp_var : str
            either 'none' or 'simple' or None for standard Lrp ,
            since 'alpha' and 'epsilon' do not make much sense, the layer defaults to 'simple' lrp
            picking flat or 'ww' defaults to 'flat'

        param : double
            the respective parameter for the lrp method of choice

        Returns
        -------
        R : the backward-propagated relevance scores.
            shaped identically to the previously processed inputs in Linear.forward
        '''

        if lrp_var is None or lrp_var.lower() == 'none' or lrp_var.lower() == 'simple':
            return self._simple_lrp(R)
        elif lrp_var.lower() == 'flat':
            return self._flat_lrp(R)
        elif lrp_var.lower() == 'ww' or lrp_var.lower() == 'w^2':
            return self._flat_lrp(R) # defaults to flat relevance projection
        elif lrp_var.lower() == 'epsilon':
            return self._simple_lrp(R) # defaults to naive variant
        elif lrp_var.lower() == 'alphabeta' or lrp_var.lower() == 'alpha':
            return self._simple_lrp(R) # defaults to naive variant
        else:
            print('Unknown lrp variant', lrp_var)



    def _simple_lrp(self,R):
        N,H,W,D = self.X.shape

        hpool,   wpool   = self.pool
        hstride, wstride = self.stride

        #assume the given pooling and stride parameters are carefully chosen.
        Hout = int((H - hpool) / hstride + 1)
        Wout = int((W - wpool) / wstride + 1)

        Rx = np.zeros_like(self.X,dtype=np.float)

        for i in range(int(Hout)):
            for j in range(int(Wout)):
                Z = self.Y[:,i:i+1,j:j+1,:] == self.X[:, i*hstride:i*hstride+hpool , j*wstride:j*wstride+wpool , : ]
                Zs = Z.sum(axis=(1,2),keepdims=True)
                Rx[:,i*hstride:i*hstride+hpool , j*wstride:j*wstride+wpool,:] += (Z / Zs) * R[:,i:i+1,j:j+1,:]
        return Rx


    def _flat_lrp(self,R):
        '''
        distribute relevance for each output evenly to the output neurons' receptive fields.
        '''
        N,H,W,D = self.X.shape

        hpool,   wpool   = self.pool
        hstride, wstride = self.stride

        #assume the given pooling and stride parameters are carefully chosen.
        Hout = int((H - hpool) / hstride + 1)
        Wout = int((W - wpool) / wstride + 1)

        Rx = np.zeros_like(self.X,dtype=np.float)

        for i in range(Hout):
            for j in range(Wout):
                Z = np.ones([N,hpool,wpool,D])
                Zs = Z.sum(axis=(1,2),keepdims=True)
                Rx[:,i*hstride:i*hstride+hpool , j*wstride:j*wstride+wpool,:] += (Z / Zs) * R[:,i:i+1,j:j+1,:]
        return Rx

    def _ww_lrp(self,R):
        '''
        There are no weights to use. default to _flat_lrp(R)
        '''
        return self._flat_lrp(R)

    def _epsilon_lrp(self,R,epsilon):
        '''
        Since there is only one (or several equally strong) dominant activations, default to _simple_lrp
        '''
        return self._simple_lrp(R)

    def _alphabeta_lrp(self,R,alpha):
        '''
        Since there is only one (or several equally strong) dominant activations, default to _simple_lrp
        '''
        return self._simple_lrp(R)