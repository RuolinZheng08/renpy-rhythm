define THIS_PATH = '00-renpythm/'

define IMG_DIR = 'images'
define TRACK_BAR_IMG = 'track_bar.png'
define HORIZONTAL_BAR_IMG = 'horizontal_bar.png'
define IMG_UP = 'arrow_up.png'
define IMG_LEFT = 'arrow_left.png'
define IMG_RIGHT = 'arrow_right.png'
define IMG_DOWN = 'arrow_down.png'

# number of track bars on which notes appear, up, left, right, down
define NUM_TRACK_BARS = 4

define SCREEN_WIDTH = 1280
define SCREEN_HEIGHT = 720
# leave some offset from the left side of the screen
define X_OFFSET = 400

define TRACK_BAR_HEIGHT = 700 # height of the track bar image
define TRACK_BAR_WIDTH = 12 # width of the track bar image
define HORIZONTAL_BAR_WIDTH = 700 # width of the horizontal bar image
define NOTE_WIDTH = 50 # width of the arrow note image

define NOTE_XOFFSET = (TRACK_BAR_WIDTH - NOTE_WIDTH) / 2

# screen definition
screen rhythm_game(filepath):
    # filepath: file path relative to renpy.config.gamedir
    default rhythm_game_displayable = RhythmGameDisplayable(filepath)

    add Solid('#000')
    add rhythm_game_displayable

    vbox xalign 0.5 yalign 0.5:
        textbutton 'play' action [
        Function(rhythm_game_displayable.play_music)
        ]

init python:
    import sys
    import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')
    sys.path.append(import_dir)

    from collections import deque

    import pygame
    from aubio import source, onset

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, filepath):
            super(RhythmGameDisplayable, self).__init__()

            self.filepath = filepath
            self.is_playing = False
            # an offset is necessary because there might be a delay between when the
            # displayable first appears on screen and the time the music starts playing
            self.time_offset = None
            # seconds, same unit as st, shown time
            file = os.path.join(renpy.config.gamedir, filepath)
            self.onset_times = deque(self.get_onset_times(file))
            # assign tracks randomly in advance since generating on the fly is too slow
            self.random_track_indices = [
            renpy.random.randint(0, NUM_TRACK_BARS - 1) for _ in range(len(self.onset_times))
            ]

            # note appear on the tracks prior to the actual onset
            # which is also the note's entire lifetime to travel the track
            self.note_offset = 2.0 # seconds
            self.note_speed = TRACK_BAR_HEIGHT / self.note_offset

            # track active notes, a list of time stamps in seconds
            self.active_notes = []

            # track number of hits for scoring
            self.num_hits = 0

            # the threshold for declaring a note as active when computing onset - (st - self.time_offset)
            self.time_difference_threshold = 0.01

            # drawables
            img_dir = os.path.join(THIS_PATH, IMG_DIR)
            self.track_bar_drawable = Image(os.path.join(img_dir, TRACK_BAR_IMG))
            self.horizontal_bar_drawable = Image(os.path.join(img_dir, HORIZONTAL_BAR_IMG))
            self.note_drawables = {
            0: Image(os.path.join(img_dir, IMG_UP)),
            1: Image(os.path.join(img_dir, IMG_LEFT)),
            2: Image(os.path.join(img_dir, IMG_RIGHT)),
            3: Image(os.path.join(img_dir, IMG_DOWN)),
            }

            # variables for drawing positions
            self.track_bar_spacing = (SCREEN_WIDTH - X_OFFSET * 2) / (NUM_TRACK_BARS - 1)
            self.horizontal_bar_xoffset = (SCREEN_WIDTH - HORIZONTAL_BAR_WIDTH) / 2
            
        def render(self, width, height, st, at):
            # cache the shown time offset
            if self.is_playing and self.time_offset is None:
                self.time_offset = st

            render = renpy.Render(width, height)
            # draw the tracks
            for track_idx in range(NUM_TRACK_BARS):
                x_offset = X_OFFSET + track_idx * self.track_bar_spacing
                render.place(self.track_bar_drawable, x=x_offset, y=0)
            # place a horizontal bar to indicate where the tracks end
            render.place(self.horizontal_bar_drawable, 
                x=self.horizontal_bar_xoffset, y=TRACK_BAR_HEIGHT)

            # draw the notes
            if self.is_playing:
                active_notes = self.get_active_notes(st)
                for note_timestamp, track_idx in active_notes:
                    x_offset = X_OFFSET + track_idx * self.track_bar_spacing + NOTE_XOFFSET
                    y_offset = TRACK_BAR_HEIGHT - note_timestamp * self.note_speed
                    arrow_drawable = self.note_drawables[track_idx]
                    render.place(arrow_drawable, x=x_offset, y=y_offset)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            return

        def visit(self):
            return []

        def play_music(self):
            self.is_playing = True
            renpy.music.play(self.filepath)

        def get_active_notes(self, st):
            active_notes = []
            for onset, track_idx in zip(self.onset_times, self.random_track_indices):
                # determine if this note is active
                time_before_appearance = onset - (st - self.time_offset)
                if time_before_appearance < 0: # already outside the screen
                    continue
                elif time_before_appearance <= self.note_offset: # should be on screen already
                    active_notes.append((time_before_appearance, track_idx))
                elif time_before_appearance - self.note_offset < self.time_difference_threshold:
                    active_notes.append((time_before_appearance, track_idx))
                elif time_before_appearance > self.note_offset: # still time before it should appear
                    break

            return active_notes

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

            return onset_times