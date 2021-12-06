define e = Character("Eileen")

label start:
    scene bg room
    e "Welcome to the Ren'Py Rhythm Game! Choose a lofi song you'd like to play."
    window hide

    # define the song titles and their files
    python:
        import os
        audio_map = {
            'Isolation': (
                'audio/Isolation.mp3',
                'audio/Isolation.beatmap.txt'
                ),
            'Positivity': (
                'audio/Positivity.mp3',
                'audio/Positivity.beatmap.txt'
                ),
            'Pearlescent': (
                'audio/Pearlescent.mp3',
                'audio/Pearlescent.beatmap.txt'
                ),
            'Thoughts': (
                'audio/Thoughts.mp3',
                'audio/Thoughts.beatmap.txt'
                )
        }
        # use a menu
        choice = renpy.display_menu(list(audio_map.items()))

    # start the rhythm game
    # window hide
    $ quick_menu = False

    # avoid rolling back and losing game state
    $ renpy.block_rollback()

    # unpack the file paths associated with the chosen song
    $ audio_path, beatmap_path = choice
    call screen rhythm_game(audio_path, beatmap_path, beatmap_stride=2)

    # avoid rolling back and entering the game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    $ num_hits, num_notes = _return
    e "You hit [num_hits] notes out of [num_notes]. Good work!"

    return
