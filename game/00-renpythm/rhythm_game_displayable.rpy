define THIS_PATH = '00-renpythm/'
define AUDIO_PATH = 'audio/'

screen rhythm_game(filepath):
    # filepath: file path relative to renpy.config.gamedir
    default rhythm_game_displayable = RhythmGameDisplayable(filepath)

    add Solid('#000')
    add rhythm_game_displayable

    vbox xalign 0.5 yalign 0.5:
        textbutton 'play' action [
        ToggleField(rhythm_game_displayable, 'is_playing'),
        Function(rhythm_game_displayable.play_music)
        ]

init python:
    import sys
    import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')
    sys.path.append(import_dir)

    from aubio import source, onset
    import numpy as np

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, filepath):
            super(RhythmGameDisplayable, self).__init__()
            self.filepath = filepath
            self.st_cache = None
            self.is_playing = False
            self.onset_times = self.get_onset_times(os.path.join(renpy.config.gamedir, filepath)) # seconds, same unit as st
            self.onset_idx = 0 # index into onset_times

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if self.is_playing and self.st_cache is None:
                self.st_cache = st
            if self.st_cache is not None:
                if self.onset_idx < len(self.onset_times):
                    print(self.onset_idx, self.onset_times[self.onset_idx])
                    val = self.onset_times[self.onset_idx]
                    diff = st - self.st_cache - val
                    if -0.02 < diff < 1:
                        render.place(Text('Onset' + str(self.onset_idx), color='#fff', size=50), x=400, y=10)
                    elif diff >= 1:
                        self.onset_idx += 1 # move on to the next onset
                render.place(Text('Timer' + str(st - self.st_cache), color='#fff', size=50), x=800, y=10)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            pass

        def visit(self):
            return []

        def play_music(self):
            renpy.music.play(self.filepath)

        # https://aubio.org/doc/latest/onset_2test-onset_8c-example.html
        # https://github.com/aubio/aubio/blob/master/python/demos/demo_onset.py
        def get_onset_times(self, filepath_abs):
            window_size = 1024 # FFT size
            hop_size = window_size // 4

            sample_rate = 0
            src_func = source(filepath_abs, sample_rate, hop_size)
            sample_rate = src_func.samplerate
            onset_func = onset('default', window_size, hop_size)
            
            onset_times = [] # seconds
            while True: # read frames
                samples, num_frames_read = src_func()
                if onset_func(samples):
                    onset_times.append(onset_func.get_last_s())
                if num_frames_read < hop_size:
                    break
            print(onset_times)
            return onset_times