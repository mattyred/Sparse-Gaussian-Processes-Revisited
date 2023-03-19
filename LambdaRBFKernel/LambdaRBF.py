import tensorflow as tf # 2.11.0
import gpflow # 2.7.0
import tensorflow_probability as tfp

class LambdaRBF(gpflow.kernels.Kernel):  
    def __init__(self, Lambda_L, variance=1.0):
        super().__init__()
        # Convert the Lambda matrix into an array (D*2,1)
        #self.Lambda = self._to_array(Lambda) TRY
        #self.Lambda = tf.gather_nd(l, indices=[[0,0], [1,1]])
        # Create a Parameter associated to Lambda matrix
        #self.L = gpflow.Parameter(L, transform=gpflow.utilities.triangular(), dtype=tf.float64, name='KernelPrecision_L')
        self.Lambda_L = gpflow.Parameter(Lambda_L, transform=gpflow.utilities.triangular(), dtype=tf.float64, name='KernelPrecision_L')
        self.variance = gpflow.Parameter(variance, transform=gpflow.utilities.positive(), dtype=tf.float64, name='KernelAmplitude')
        #self.Kxx = tf.Variable(np.empty((N, N), dtype=np.float64), name='KernelMatrix')

    def K(self, X, X2=None):
        """
            X: matrix NxD
            X2: matrix NxD
            ---
            Returns Kernel matrix as a 2D tensor
        """
        if X2 is None:
            X2 = X
        N = X.shape[0]
        #Lambda = self._to_matrix(self.Lambda) TRY
        Lambda = tf.linalg.matmul(self.Lambda_L, tf.transpose(self.Lambda_L)) # recover LLᵀ

        # compute z, z2
        z = self._z(X, Lambda)
        z2 = self._z(X2, Lambda)
        # compute X(X2Λ)ᵀ
        X2Lambda = tf.linalg.matmul(X, Lambda)
        XX2LambdaT = tf.linalg.matmul(X, tf.transpose(X2Lambda))
        # compute z1ᵀ 
        ones = tf.ones(shape=(N,1), dtype=tf.float64)
        zcol = tf.linalg.matmul(z, tf.transpose(ones))
        # compute 1z2ᵀ 
        zrow = tf.linalg.matmul(ones, tf.transpose(z2))

        exp_arg = zcol - 2*XX2LambdaT + zrow
        Kxx = tf.math.exp(-0.5 * exp_arg)
        return self.variance * Kxx
    
    def K_diag(self, X):
        return self.variance * tf.reshape(X, (-1,))  # this returns a 1D tensor
    
    def _z(self, X, Lambda):
        XLambda = tf.linalg.matmul(X, Lambda)
        XLambdaX = tf.math.multiply(XLambda, X)
        return tf.math.reduce_sum(XLambdaX, axis=1, keepdims=True)
    
    def _to_array(self, L):
        D = tf.shape(L).numpy()[0]
        return tf.reshape(L, [D*2,1])
    
    def _to_matrix(self, l):
        D = int(tf.shape(l).numpy()[0]/2)
        return tf.reshape(l, [D,D])