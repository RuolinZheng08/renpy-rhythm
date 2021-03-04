define THIS_PATH = '00-renpythm/'
define AUDIO_PATH = 'audio/'

screen rhythm_game(filepath):
    # filepath: file path relative to renpy.config.gamedir
    default rhythm_game_displayable = RhythmGameDisplayable(filepath)

    add Solid('#000')
    add rhythm_game_displayable

    vbox xalign 0.5 yalign 0.5:
        textbutton 'play' action Function(rhythm_game_displayable.play_music)

init python:
    import sys
    import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')
    sys.path.append(import_dir)

    from aubio import source, onset

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, filepath):
            super(RhythmGameDisplayable, self).__init__()
            self.filepath = filepath
            self.filepath_abs = os.path.join(renpy.config.gamedir, filepath)
            self.t = Text('')
            
        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            render.place(self.t, x=1020, y=10)
            return render

        def event(self, ev, x, y, st):
            self.t = Text('hello'+str(st), color='#fff', size=50)
            renpy.redraw(self, 0)

        def visit(self):
            return []

        def play_music(self):
            renpy.music.play(self.filepath)

        # https://aubio.org/doc/latest/onset_2test-onset_8c-example.html
        # https://github.com/aubio/aubio/blob/master/python/demos/demo_onset.py
        def get_onset_times(self):
            window_size = 1024 # FFT size
            hop_size = window_size // 4

            sample_rate = 0
            src_func = source(self.filepath_abs, sample_rate, hop_size)
            sample_rate = src_func.samplerate
            onset_func = onset('default', window_size, hop_size)
            
            onset_times = [] # seconds
            while True: # read frames
                samples, num_frames_read = src_func()
                if onset_func(samples):
                    onset_times.append(onset_func.get_last_s())
                if num_frames_read < hop_size:
                    break

            return onset_times