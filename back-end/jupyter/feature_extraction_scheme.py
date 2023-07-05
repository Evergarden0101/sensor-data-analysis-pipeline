import pandas as pd
from digital_processing import bp_filter, notch_filter, plot_signal
from feature_extraction import features_estimation

# Load data
signal_path = './back-end/data/1022102cFnorm.csv'
emg_signal = pd.read_csv(signal_path).iloc[:60000,:3].values
channel_name = 'EMG Signals'
sampling_frequency = 2e3
frame = 500
step = 250


# Plot raw sEMG signal
plot_signal(emg_signal, sampling_frequency, channel_name)

# Biomedical Signal Processing
emg_signal = emg_signal.reshape((emg_signal.size,))
filtered_signal = notch_filter(emg_signal, sampling_frequency,
                               True)
filtered_signal = bp_filter(filtered_signal, 10, 500,
                            sampling_frequency, True)

# EMG Feature Extraction
emg_features, features_names = features_estimation(filtered_signal, channel_name,
                                                   sampling_frequency, frame, step, False)
print(emg_features)
print(features_names)
emg_features.T.to_csv("./back-end/output/emg_feature.csv")