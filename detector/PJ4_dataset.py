import sys

import numpy as np
import scipy
import librosa


class SpeakerDataset:
    def __init__(self,
                 *,
                 n_fft=512,
                 win_len_time=0.02,
                 hop_len_time=0.01,
                 fs=16000,
                 n_coeff=64,
                 fr_len=150):
        self.win_sample = int(win_len_time * fs)
        self.hop_sample = int(hop_len_time * fs)
        self.n_fft = n_fft
        self.fs = fs
        self.n_coeff = n_coeff
        self.eps = np.array(sys.float_info.epsilon)
        self.max_fr = fr_len

    # Combine features depending on the context window setup.
    def _context_window(self, *, feature, left, right):
        context_feature = []
        for i in range(left, len(feature) - right):
            feat = np.concatenate((feature[i - left:i + right]), axis=-1)
            context_feature.append(feat)
        context_feature = np.vstack(context_feature)
        return context_feature

    # Compute input features and concatenate depending on the type of context window.
    def get_feature(self, sig):
        stft = librosa.core.stft(sig, n_fft=self.n_fft, hop_length=self.hop_sample, win_length=self.win_sample)
        feature = abs(stft).transpose()

        mel_fb = librosa.filters.mel(self.fs, n_fft=self.n_fft, n_mels=self.n_coeff)
        power = feature ** 2
        feature = np.matmul(power, mel_fb.transpose())
        feature = 10 * np.log10(feature + self.eps)
        feature = scipy.fft.dct(feature, axis=-1, norm='ortho')
        delta = librosa.feature.delta(feature)
        delta2 = librosa.feature.delta(feature, order=2)
        feature = np.concatenate((feature, delta, delta2), axis=-1)

        feature = self._context_window(feature=feature, left=5, right=5)
        return feature
