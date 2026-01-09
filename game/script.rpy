define e = Character("DJ Master")

# define video_bg = "video/think_about_us_vid.webm"

init python early:
    import os
    config.log = os.path.join(config.basedir, "davids_log.txt")


# define the song titles and their files
init python:
    # must be persistent to be able to record the scores
    # after adding new songs, please remember to delete the persistent data

    rhythm_game_songs = [
    Song('Think About Us', 'audio/think_about_us.mp3', 'audio/think_about_us.beatmap.txt', beatmap_stride=2),
    Song('Wide Open', 'audio/wide_open.mp3', 'audio/wide_open.beatmap.v2.txt', beatmap_stride=3),
    Song('Feisty', 'audio/feisty.mp3','audio/feisty_labelsv3.txt',beatmap_stride=2)
    # Song('Isolation', 'audio/Isolation.mp3', 'audio/Isolation.beatmap.txt')
    # Song('Positivity', 'audio/Positivity.mp3', 'audio/Positivity.beatmap.txt'),
    # Song('Pearlescent', 'audio/Pearlescent.mp3', 'audio/Pearlescent.beatmap.txt'),
    # Song('Pearlescent - trimmed', 'audio/Pearlescent - trimmed.mp3', 'audio/Pearlescent - trimmed.beatmap.txt'), # 22 sec, easy to test 
    # Song('Thoughts', 'audio/Thoughts.mp3', 'audio/Thoughts.beatmap.txt')
    ]

init python:
    # Ensure the dict exists
    if not isinstance(getattr(persistent, "rhythm_game_high_scores", None), dict):
        persistent.rhythm_game_high_scores = {}

    def reset_persistent(do_reset=False):
        if do_reset:
            persistent.rhythm_game_high_scores = {}

        # Seed missing songs safely
        for s in rhythm_game_songs:
            persistent.rhythm_game_high_scores.setdefault(s.name, (0, 0.0))
        
        renpy.save_persistent()

    
    
    # Run once on startup (no reset)
    reset_persistent(False)


$ renpy.log(f"score keys: {list(persistent.rhythm_game_high_scores.keys())}")
$ renpy.log(f"song names: {[s.name for s in rhythm_game_songs]}")            


# the song that the player chooses to play, set in `choose_song_screen` below
default selected_song = None
image bg room2 = im.Scale("images/bgroom2.png", config.screen_width, config.screen_height)


label start:
    scene bg room2

    e "Welcome to DJ Simulator!"

    window hide
    call rhythm_game_entry_label

    e "Nice work hitting those notes! Hope you enjoyed the game."

    return

# a simpler way to launch the minigame 
label test:
    e "Welcome to Dj Simulator!"
    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    $ song = Song('Think about us', 'audio/think_about_us.mp3', 'audio/think_about_us.beatmap.txt', beatmap_stride=3)
    $ rhythm_game_displayable = RhythmGameDisplayable(song)
    call screen rhythm_game(rhythm_game_displayable, video_bg)

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    return
