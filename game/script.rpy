define e = Character("Eileen")

# define the song titles and their files
init python:
    songs = [
    Song('Isolation', 'audio/Isolation.mp3', 'audio/Isolation.beatmap.txt'),
    Song('Positivity', 'audio/Positivity.mp3', 'audio/Positivity.beatmap.txt'),
    Song('Pearlescent', 'audio/Pearlescent.mp3', 'audio/Pearlescent.beatmap.txt'),
    Song('Thoughts', 'audio/Thoughts.mp3', 'audio/Thoughts.beatmap.txt')
    ]

label start:
    scene bg room
    e "Welcome to the Ren'Py Rhythm Game! Choose a lofi song you'd like to play."
    window hide
    
    # start the rhythm game
    # window hide
    $ quick_menu = False

    # avoid rolling back and losing game state
    $ renpy.block_rollback()

    # disable Esc key menu to prevent the player from saving the game
    $ _game_menu_screen = None

    call screen choose_song_screen(songs)

    # re-enable the Esc key menu
    $ _game_menu_screen = 'save'

    # avoid rolling back and entering the game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    # $ num_hits, num_notes = _return
    # e "You hit [num_hits] notes out of [num_notes]. Good work!"
    e 'TBD'

    return
