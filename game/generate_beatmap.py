import os
import sys

# python-packages directory
import_dir = os.path.abspath('python-packages')
sys.path.append(import_dir)

from aubio import source, onset

# https://aubio.org/doc/latest/onset_2test-onset_8c-example.html
# https://github.com/aubio/aubio/blob/master/python/demos/demo_onset.py
# https://aubio.org/manual/latest/py_io.html
def get_onset_times(file_path):
    window_size = 1024 # FFT size
    hop_size = window_size // 4

    sample_rate = 0
    src_func = source(file_path, sample_rate, hop_size)
    sample_rate = src_func.samplerate
    onset_func = onset('default', window_size, hop_size)
    
    duration = float(src_func.duration) / src_func.samplerate

    onset_times = [] # seconds
    while True: # read frames
        samples, num_frames_read = src_func()
        if onset_func(samples):
            onset_time = onset_func.get_last_s()
            if onset_time < duration:
                onset_times.append(onset_time)
            else:
                break
        if num_frames_read < hop_size:
            break
    
    return onset_times

def main():
    if len(sys.argv) < 2:
        print('Usage: python generate_beatmap.py [input]\nGenerate my_music.beatmap.txt form my_music.mp3\n[input] could be a file or directory containing audio files')
    path = sys.argv[1]
    if os.path.isdir(path):
        files = [os.path.join(path, file) for file in os.listdir(path) if not file.startswith('.')]
    else: # a single file
        files = [path]

    for file_path in files:
        try:
            onset_times = get_onset_times(file_path)
            # remove extension, .mp3, .wav etc.
            file_name_no_extension, _ = os.path.splitext(file_path)
            output_name = file_name_no_extension + '.beatmap.txt'
            with open(output_name, 'wt') as f:
                f.write('\n'.join(['%.4f' % onset_time for onset_time in onset_times]))
            print(file_path + ' => ' + output_name)
        except Exception as e:
            print('Error processing ' + file_path + '\n' + str(e))

if __name__ == '__main__':
    main()