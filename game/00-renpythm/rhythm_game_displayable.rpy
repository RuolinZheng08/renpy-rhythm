define THIS_PATH = '00-renpythm/'

define IMG_DIR = 'images'
define IMG_UP = 'up.png'
define IMG_LEFT = 'left.png'
define IMG_RIGHT = 'right.png'
define IMG_DOWN = 'down.png'

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

            # zoom the note when it is within the hit threshold
            self.zoom_scale = 1.2

            # offset for rendering
            # leave some offset from the left side of the screen
            self.x_offset = 400
            self.track_bar_height = int(config.screen_height * 0.9)
            self.track_bar_width = 12
            self.horizontal_bar_height = 12
            self.note_width = 50 # width of the note image
            self.note_xoffset = (self.track_bar_width - self.note_width) / 2
            self.note_xoffset_large = (self.track_bar_width - self.note_width * self.zoom_scale) / 2

            # note appear on the tracks prior to the actual onset
            # which is also the note's entire lifetime to travel the track
            self.note_offset = 3.0 # seconds
            self.note_speed = self.track_bar_height / self.note_offset

            # silence before the music plays
            self.silence_offset = 3.0
            self.silence = '<silence %s>' % str(self.silence_offset)

            # an offset is necessary because there might be a delay between when the
            # displayable first appears on screen and the time the music starts playing
            # seconds, same unit as st, shown time
            self.time_offset = None

            # limit the number of notes
            self.num_notes_threshold = 300

            # number of track bars
            self.num_track_bars = 4

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
            renpy.random.randint(0, self.num_track_bars - 1) for _ in range(len(self.onset_times))
            ]

            # a list active note timestamps on each track
            self.active_notes_per_track = {track_idx: [] for track_idx in range(self.num_track_bars)}

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
            self.track_bar_drawable = Solid('#fff', xsize=self.track_bar_width, ysize=self.track_bar_height)
            self.horizontal_bar_drawable = Solid('#fff', xsize=config.screen_width, ysize=self.horizontal_bar_height)

            self.note_drawables = {
            0: Image(os.path.join(img_dir, IMG_UP)),
            1: Image(os.path.join(img_dir, IMG_LEFT)),
            2: Image(os.path.join(img_dir, IMG_RIGHT)),
            3: Image(os.path.join(img_dir, IMG_DOWN)),
            }

            self.note_drawables_large = {
            0: Transform(self.note_drawables[0], zoom=self.zoom_scale),
            1: Transform(self.note_drawables[1], zoom=self.zoom_scale),
            2: Transform(self.note_drawables[2], zoom=self.zoom_scale),
            3: Transform(self.note_drawables[3], zoom=self.zoom_scale),
            }

            # variables for drawing positions
            self.track_bar_spacing = (config.screen_width - self.x_offset * 2) / (self.num_track_bars - 1)

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
            for track_idx in range(self.num_track_bars):
                x_offset = self.x_offset + track_idx * self.track_bar_spacing
                render.place(self.track_bar_drawable, x=x_offset, y=0)
            # place a horizontal bar to indicate where the tracks end
            render.place(self.horizontal_bar_drawable, x=0, y=self.track_bar_height)

            # draw the notes
            curr_time = st - self.time_offset
            if self.is_playing:
                self.active_notes_per_track = self.get_active_notes(st)
                for track_idx in self.active_notes_per_track:
                    x_offset = self.x_offset + track_idx * self.track_bar_spacing

                    for onset, note_timestamp in self.active_notes_per_track[track_idx]:
                        if self.onset_hits[onset] is False: # hasn't been hit, render
                            # enlarge the note if it is now within the hit threshold
                            if onset - self.hit_threshold <= curr_time <= onset + self.hit_threshold:
                                note_drawable = self.note_drawables_large[track_idx]
                                note_xoffset = x_offset + self.note_xoffset_large 
                            else:
                                note_drawable = self.note_drawables[track_idx]
                                note_xoffset = x_offset + self.note_xoffset 

                            y_offset = self.track_bar_height - note_timestamp * self.note_speed
                            render.place(note_drawable, x=note_xoffset, y=y_offset)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            if ev.type == pygame.KEYDOWN:
                if not ev.key in self.keycode_to_track_idx:
                    return
                curr_time = st - self.time_offset
                track_idx = self.keycode_to_track_idx[ev.key]
                active_notes_on_track = self.active_notes_per_track[track_idx]

                for note in active_notes_on_track:
                    onset, _ = note
                    # time when player attempts to hit the note
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
            active_notes = {track_idx: [] for track_idx in range(self.num_track_bars)}
            for onset, track_idx in zip(self.onset_times, self.random_track_indices):
                # determine if this note is active
                time_before_appearance = onset - (st - self.time_offset)
                if time_before_appearance < 0: # already outside the screen
                    continue
                # should be on screen already
                elif time_before_appearance <= self.note_offset:
                    active_notes[track_idx].append((onset, time_before_appearance))
                # within threshold
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