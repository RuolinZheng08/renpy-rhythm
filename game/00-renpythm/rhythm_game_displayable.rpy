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
    import pygame

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, filepath):
            super(RhythmGameDisplayable, self).__init__()
            self.filepath = filepath
            self.st_cache = None
            self.is_playing = False
            self.onset_times = self.get_onset_times(os.path.join(renpy.config.gamedir, filepath)) # seconds, same unit as st
            self.onset_idx = 0 # index into onset_times
            self.onset_drawable = Image(os.path.join(THIS_PATH, 'images', 'circle.png'))
            self.highlight_drawable = Image(os.path.join(THIS_PATH, 'images', 'circle_highlight.png'))

            self.onset_xpos = renpy.random.randint(200, 1000)
            self.onset_ypos = renpy.random.randint(200, 500)
            self.onset_drawable_diameter = 200
            self.has_hit = False

            self.num_hits = 0

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if self.is_playing and self.st_cache is None:
                self.st_cache = st
            if self.st_cache is not None:
                if self.onset_idx < len(self.onset_times):
                    # print(self.onset_idx, self.onset_times[self.onset_idx])
                    val = self.onset_times[self.onset_idx]
                    diff = st - self.st_cache - val
                    if -0.02 < diff < 1:
                        render.place(Text('Onset' + str(self.onset_idx), color='#fff', size=50), x=400, y=10)
                        if not self.has_hit:
                            render.place(self.onset_drawable, x=self.onset_xpos, y=self.onset_ypos)
                        else:
                            render.place(Text('GOOD!', color='#fff', size=50), x=650, y=40)
                            render.place(self.highlight_drawable, x=self.onset_xpos, y=self.onset_ypos)
                            
                    elif diff >= 1:
                        self.has_hit = False
                        self.onset_idx += 1 # move on to the next onset
                        # regenerate random pos
                        self.onset_xpos = renpy.random.randint(200, 1000)
                        self.onset_ypos = renpy.random.randint(200, 500)

                render.place(Text('Timer ' + str(st - self.st_cache), color='#fff', size=50), x=800, y=10)
                render.place(Text('Num hits: ' + str(self.num_hits), color='#fff', size=50), x=20, y=10)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            # check if player is clicking on the right position
            # print(x, self.onset_xpos, y, self.onset_ypos)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if -10 <= x - self.onset_xpos <= self.onset_drawable_diameter and \
                -10 <= y - self.onset_ypos <= self.onset_drawable_diameter:
                    self.has_hit = True
                    self.num_hits += 1
                else:
                    self.has_hit = False
                    
            renpy.redraw(self, 0)

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