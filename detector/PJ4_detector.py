import torch
import numpy as np
from PJ4_dataset import SpeakerDataset
from PJ4_model import Dvector


def load_model():
    # Check if we can use a GPU device.
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    # Set parameter
    n_coeff = 13  # feature dimension
    n_spk = 4  # number of speakers in the dataset
    in_dim = n_coeff * 3  # input dimension (MFCC, delta, delta-delta)
    context_len = 10  # number of context window
    out_dim = 512  # d-vector output dimension
    model_path = 'model/model_opt.pth'

    # Get model
    model = Dvector(n_spk, in_dim * context_len, out_dim).to(device)
    check = torch.load(model_path)
    model.load_state_dict(check['model'])

    return model


def find_who(model, sig):
    # Set parameter
    n_coeff = 13  # feature dimension
    labels = ['양정일', '이정재', '지동근', '나휘연']

    # Check if we can use a GPU device.
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    # Load data
    dataset = SpeakerDataset(n_coeff=n_coeff)
    feature = dataset.get_feature(sig)
    feature = feature[:70, :]
    feature = np.expand_dims(feature, axis=0)
    feature = torch.from_numpy(feature)
    data = feature.to(device)

    model.eval()
    pred = model(data, extract=True)

    print(pred)

    return labels[torch.argmax(pred).item()]
