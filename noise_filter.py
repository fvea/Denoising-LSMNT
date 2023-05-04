from functs import *
import argparse
import librosa
import sounddevice as sd
import os

def main(args):

   # Parse given arguments
    wav_filepath = os.path.abspath(args.wav_file)
    sr = args.sr; rpm = args.speed; balls = args.balls

    # Load the signal from the wav file argument
    signal, sr = librosa.load(wav_filepath, sr=sr)

    # Decompose signal using Empirical Mode Decomposition (EMD)
    print("Decomposing signal...")
    imfs, _, _ = emd_denoise(signal)

    # Play an IMF
    num_imfs = len(imfs)
    print(num_imfs)

    print("Done.")
    plot_emd_result(signal, sr, imfs)  # plot the results

    while True:
        # Ask the user to select an IMF
        user_input = input(f"Enter an IMF number to play (0-{num_imfs-2}), or '-1' to play the unfiltered audio or 'q' to quit: ")
        if user_input == 'q':
            break

        # handle invalid input
        try:
            imf_idx = int(user_input)
            if (imf_idx < -1) or (imf_idx > num_imfs - 2):
                raise ValueError()
        except ValueError:
            print(f"Invalid input. Please enter a number between -1 and {num_imfs-2}, or 'q' to quit.")
            continue

        # play the selected IMF
        imf_data = imfs[imf_idx] if not imf_idx == -1 else signal
        _ = sd.play(imf_data, sr, blocking=False)

        # plot the imf envelope signal and fft
        plot_envelope_signal(imf_data, sr, imf_idx=imf_idx, rpm=rpm, num_balls=balls)
    
       # Ask the user to stop the audio playing
        stop_streaming = False
        while not stop_streaming:
            stop_audio = input("Press 'x' to stop the audio: ")
            if stop_audio.lower() == 'x':
                sd.stop()
                plt.close(plt.gcf()) # close the envelope signal plot
                stop_streaming = True


if __name__ == '__main__':
    # set arguments
    parser = argparse.ArgumentParser(description='Empirical Mode Decomposition Noise Filter')
    parser.add_argument('-f', '--wav_file', dest='wav_file', type=str, required=True, help='WAV Filepath')
    parser.add_argument('-sr', '--sample_rate', dest='sr', type=int, default=11025, help='Sample Rate')
    parser.add_argument('-s', '--speed', dest='speed', type=int, default=None, help='Bearing speed in RPM')
    parser.add_argument('-b', '--balls', dest='balls', type=int, default=None, help='Bearing # of balls')
    args = parser.parse_args()
    main(args)