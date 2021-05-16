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
        
    showif rhythm_game_displayable.is_playing:
        fixed xpos 50 ypos 50 spacing 100:
            vbox:
                text 'Hits: ' + str(rhythm_game_displayable.num_hits):
                     color '#fff'

init python:
    import sys
    import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')
    sys.path.append(import_dir)

    import random
    import pygame
    from aubio import source, onset

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, filepath):
            super(RhythmGameDisplayable, self).__init__()

            self.filepath = filepath

            self.is_playing = False

            # note appear on the tracks prior to the actual onset
            # which is also the note's entire lifetime to travel the track
            self.note_offset = 3.0 # seconds
            self.note_speed = TRACK_BAR_HEIGHT / self.note_offset

            # silence before the music plays
            self.silence_offset = 3.0
            self.silence = '<silence %s>' % str(self.silence_offset)

            # an offset is necessary because there might be a delay between when the
            # displayable first appears on screen and the time the music starts playing
            # seconds, same unit as st, shown time
            self.time_offset = None

            # limit the number of notes
            self.num_notes_threshold = 300

            file = os.path.join(renpy.config.gamedir, filepath)
            # onset timestamps in the given audio file
            onset_times = self.get_onset_times(file)
            if len(onset_times) > self.num_notes_threshold:
                onset_times = random.sample(onset_times, self.num_notes_threshold)
                onset_times.sort()
            # increment by the silence time
            self.onset_times = [self.silence_offset + onset for onset in onset_times]

            # whether an onset been hit determines whether it will be rendered
            self.onset_hits = {onset: False for onset in self.onset_times}
            # assign tracks randomly in advance since generating on the fly is too slow
            self.random_track_indices = [
            renpy.random.randint(0, NUM_TRACK_BARS - 1) for _ in range(len(self.onset_times))
            ]

            # a list active note timestamps on each track
            self.active_notes_per_track = {track_idx: [] for track_idx in range(NUM_TRACK_BARS)}

            # track number of hits for scoring
            self.num_hits = 0

            # the threshold for declaring a note as active when computing onset - (st - self.time_offset)
            self.time_difference_threshold = 0.01
            # the threshold for considering a note as hit
            self.hit_threshold = 0.2

            # map pygame key code to track idx
            self.keycode_to_track_idx = {
            pygame.K_UP: 0,
            pygame.K_LEFT: 1,
            pygame.K_RIGHT: 2,
            pygame.K_DOWN: 3
            }

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

            # start playing music
            self.play_music()
            
        def render(self, width, height, st, at):
            # cache the shown time offset
            if self.is_playing and self.time_offset is None:
                self.time_offset = self.silence_offset + st

            render = renpy.Render(width, height)

            # count down silence_offset, 3 seconds, while silence
            countdown = None
            time_before_music = self.silence_offset - st
            if time_before_music > 2.0:
                countdown = '3'
            elif time_before_music > 1.0:
                countdown = '2'
            elif time_before_music > 0.0:
                countdown = '1'
            if countdown is not None:
                render.place(Text(countdown, color='#fff', size=48),
                    x=config.screen_width / 2, y=config.screen_height / 2)

            # draw the tracks
            for track_idx in range(NUM_TRACK_BARS):
                x_offset = X_OFFSET + track_idx * self.track_bar_spacing
                render.place(self.track_bar_drawable, x=x_offset, y=0)
            # place a horizontal bar to indicate where the tracks end
            render.place(self.horizontal_bar_drawable, 
                x=self.horizontal_bar_xoffset, y=TRACK_BAR_HEIGHT)

            # draw the notes
            if self.is_playing:
                self.active_notes_per_track = self.get_active_notes(st)
                for track_idx in self.active_notes_per_track:
                    note_drawable = self.note_drawables[track_idx]
                    x_offset = X_OFFSET + track_idx * self.track_bar_spacing + NOTE_XOFFSET

                    for onset, note_timestamp in self.active_notes_per_track[track_idx]:
                        if self.onset_hits[onset] is False: # hasn't been hit, render
                            y_offset = TRACK_BAR_HEIGHT - note_timestamp * self.note_speed
                            render.place(note_drawable, x=x_offset, y=y_offset)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            if ev.type == pygame.KEYDOWN:
                if not ev.key in self.keycode_to_track_idx:
                    return
                track_idx = self.keycode_to_track_idx[ev.key]
                active_notes_on_track = self.active_notes_per_track[track_idx]

                for note in active_notes_on_track:
                    onset, _ = note
                    # time when player attempts to hit the note
                    curr_time = st - self.time_offset
                    # difference between the time the note is hittable and actually hit
                    if onset - self.hit_threshold <= curr_time <= onset + self.hit_threshold:
                        self.onset_hits[onset] = True
                        self.num_hits += 1
                        renpy.redraw(self, 0)
                        renpy.restart_interaction() # force refresh the screen for score to show

        def visit(self):
            return []

        def play_music(self):
            renpy.music.queue([self.silence, self.filepath])
            self.is_playing = True

        def get_active_notes(self, st):
            active_notes = {track_idx: [] for track_idx in range(NUM_TRACK_BARS)}
            for onset, track_idx in zip(self.onset_times, self.random_track_indices):
                # determine if this note is active
                time_before_appearance = onset - (st - self.time_offset)
                if time_before_appearance < 0: # already outside the screen
                    continue
                elif time_before_appearance <= self.note_offset: # should be on screen already
                    active_notes[track_idx].append((onset, time_before_appearance))
                elif time_before_appearance - self.note_offset < self.time_difference_threshold:
                    active_notes[track_idx].append((onset, time_before_appearance))
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