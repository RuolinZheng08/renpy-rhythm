# Note: the terms onset and beatmap are used interchangeably in this script

define THIS_PATH = '00-renpythm/'

define IMG_DIR = 'images/'
define IMG_UP = THIS_PATH + IMG_DIR + 'up.png'
define IMG_LEFT = THIS_PATH + IMG_DIR + 'left.png'
define IMG_RIGHT = THIS_PATH + IMG_DIR + 'right.png'
define IMG_DOWN = THIS_PATH + IMG_DIR + 'down.png'

# screen definition
screen rhythm_game(audio_path, beatmap_path, beatmap_stride=None):
    # audio_path (str): file path relative to renpy.config.gamedir
    default rhythm_game_displayable = RhythmGameDisplayable(
        audio_path, beatmap_path, beatmap_stride=beatmap_stride)

    add Solid('#000')
    add rhythm_game_displayable
    if rhythm_game_displayable.has_ended:
        # use a timer so the player can see the screen once again
        timer 2.0 action [Return(
            (rhythm_game_displayable.num_hits, 
                rhythm_game_displayable.num_notes)
            )]
        
    showif rhythm_game_displayable.has_started:
        fixed xpos 50 ypos 50 spacing 100:
            vbox:
                text 'Hits: ' + str(rhythm_game_displayable.num_hits):
                     color '#fff'

init python:
    import random
    import pygame

    class RhythmGameDisplayable(renpy.Displayable):

        def __init__(self, audio_path, beatmap_path, beatmap_stride=None):
            """
            beatmap_stride (int): Default to 2. Use onset_times[::beatmap_stride] so that the tracks don't get too crowded. Can be used to set difficulty level
            """
            super(RhythmGameDisplayable, self).__init__()

            self.audio_path = audio_path

            self.has_started = False
            self.has_ended = False

            # zoom the note when it is within the hit threshold
            self.zoom_scale = 1.2

            # offset for rendering
            # leave some offset from the left side of the screen
            self.x_offset = 400
            self.track_bar_height = int(config.screen_height * 0.85)
            self.track_bar_width = 12
            self.horizontal_bar_height = 8
            self.note_width = 50 # width of the note image
            self.note_xoffset = (self.track_bar_width - self.note_width) / 2
            self.note_xoffset_large = (self.track_bar_width - self.note_width * self.zoom_scale) / 2
            # place the hit text some spacing from the end of the track bar
            self.hit_text_yoffset = 30

            # note appear on the tracks prior to the actual onset
            # which is also the note's entire lifetime to travel the entire screen
            # can be used to set difficulty level of the game
            self.note_offset = 3.0 # seconds
            self.note_speed = config.screen_height / self.note_offset

            # an offset is necessary because there might be a delay between when the
            # displayable first appears on screen and the time the music starts playing
            # seconds, same unit as st, shown time
            self.time_offset = None

            # number of track bars
            self.num_track_bars = 4

            # silence before the music plays
            self.silence_offset_start = 4.5
            self.silence_start = '<silence %s>' % str(self.silence_offset_start)
            # count down before the music plays
            self.countdown = 3.0

            # onset timestamps in the beatmap file given audio file
            onset_times = self.read_beatmap_file(beatmap_path)
            # take strides throught onset_times so that the tracks don't get too crowded
            if beatmap_stride is None:
                beatmap_stride = 2
            self.onset_times = onset_times[::beatmap_stride]

            # whether an onset been hit determines whether it will be rendered
            self.onset_hits = {onset: False for onset in self.onset_times}
            self.num_notes = len(self.onset_times)
            # assign tracks randomly in advance since generating on the fly is too slow
            self.random_track_indices = [
            renpy.random.randint(0, self.num_track_bars - 1) for _ in range(self.num_notes)
            ]

            # a list active note timestamps on each track
            self.active_notes_per_track = {track_idx: [] for track_idx in range(self.num_track_bars)}

            # track number of hits for scoring
            self.num_hits = 0

            # the threshold for declaring a note as active when computing onset - (st - self.time_offset)
            self.time_difference_threshold = 0.01
            # the threshold for considering a note as hit
            self.hit_threshold = 0.3

            # map pygame key code to track idx
            self.keycode_to_track_idx = {
            pygame.K_LEFT: 0,
            pygame.K_UP: 1,
            pygame.K_DOWN: 2,
            pygame.K_RIGHT: 3
            }

            # drawables
            self.hit_text_drawable = Text('Hit!', color='#fff')

            self.track_bar_drawable = Solid('#fff', xsize=self.track_bar_width, ysize=self.track_bar_height)
            self.horizontal_bar_drawable = Solid('#fff', xsize=config.screen_width, ysize=self.horizontal_bar_height)

            self.note_drawables = {
            0: Image(IMG_LEFT),
            1: Image(IMG_UP),
            2: Image(IMG_DOWN),
            3: Image(IMG_RIGHT),
            }

            self.note_drawables_large = {
            0: Transform(self.note_drawables[0], zoom=self.zoom_scale),
            1: Transform(self.note_drawables[1], zoom=self.zoom_scale),
            2: Transform(self.note_drawables[2], zoom=self.zoom_scale),
            3: Transform(self.note_drawables[3], zoom=self.zoom_scale),
            }

            # for self.visit method
            self.drawables = [
            self.hit_text_drawable, 
            self.track_bar_drawable, 
            self.horizontal_bar_drawable
            ]
            self.drawables.extend(list(self.note_drawables.values()))
            self.drawables.extend(list(self.note_drawables_large.values()))

            # variables for drawing positions
            self.track_bar_spacing = (config.screen_width - self.x_offset * 2) / (self.num_track_bars - 1)

            # start playing music
            self.play_music()
            
        def render(self, width, height, st, at):
            # cache the shown time offset
            if self.has_started and self.time_offset is None:
                self.time_offset = self.silence_offset_start + st

            render = renpy.Render(width, height)

            # count down silence_offset_start, 3 seconds, while silence
            countdown_text = None
            time_before_music = self.countdown - st
            if time_before_music > 2.0:
                countdown_text = '3'
            elif time_before_music > 1.0:
                countdown_text = '2'
            elif time_before_music > 0.0:
                countdown_text = '1'
            if countdown_text is not None:
                render.place(Text(countdown_text, color='#fff', size=48),
                    x=config.screen_width / 2, y=config.screen_height / 2)

            # draw the tracks
            for track_idx in range(self.num_track_bars):
                x_offset = self.x_offset + track_idx * self.track_bar_spacing
                render.place(self.track_bar_drawable, x=x_offset, y=0)
            # place a horizontal bar to indicate where the tracks end
            render.place(self.horizontal_bar_drawable, x=0, y=self.track_bar_height)

            if self.has_started:
                # if song has ended, return
                if renpy.music.get_playing() is None:
                    self.has_ended = True
                    renpy.timeout(0) # raise event
                    # no need to draw notes
                    renpy.redraw(self, 0)
                    return render

                # draw notes
                curr_time = st - self.time_offset
                self.active_notes_per_track = self.get_active_notes(st)
                for track_idx in self.active_notes_per_track:
                    x_offset = self.x_offset + track_idx * self.track_bar_spacing

                    for onset, note_timestamp in self.active_notes_per_track[track_idx]:
                        if self.onset_hits[onset] is False: # hasn't been hit, render
                            # enlarge the note if it is now within the hit threshold
                            if abs(curr_time - onset) <= self.hit_threshold:
                                note_drawable = self.note_drawables_large[track_idx]
                                note_xoffset = x_offset + self.note_xoffset_large 
                            else:
                                note_drawable = self.note_drawables[track_idx]
                                note_xoffset = x_offset + self.note_xoffset 

                            y_offset = self.track_bar_height - note_timestamp * self.note_speed
                            render.place(note_drawable, x=note_xoffset, y=y_offset)
                        else: # show hit text
                            render.place(self.hit_text_drawable, x=x_offset, y=self.track_bar_height + self.hit_text_yoffset)

            renpy.redraw(self, 0)
            return render

        def event(self, ev, x, y, st):
            if self.has_ended: # no need to handle more events
                renpy.restart_interaction() # force refresh the screen to detect end game
                return
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
                    if abs(curr_time - onset) <= self.hit_threshold:
                        self.onset_hits[onset] = True
                        self.num_hits += 1
                        renpy.redraw(self, 0)
                        renpy.restart_interaction() # force refresh the screen for score to show

        def visit(self):
            # visit all drawables
            return self.drawables

        def play_music(self):
            renpy.music.queue([self.silence_start, self.audio_path], loop=False)
            self.has_started = True

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
                elif abs(time_before_appearance - self.note_offset) < self.time_difference_threshold:
                    active_notes[track_idx].append((onset, time_before_appearance))
                elif time_before_appearance > self.note_offset: # still time before it should appear
                    break

            return active_notes

        def read_beatmap_file(self, beatmap_path):
            # read newline separated floats
            beatmap_path_full = os.path.join(config.gamedir, beatmap_path)
            with open(beatmap_path_full, 'rt') as f:
                text = f.read()
            onset_times = [float(string) for string in text.split('\n') if string != '']
            return onset_times