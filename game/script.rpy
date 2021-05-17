# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

label start:
    scene bg room
    e "Welcome to the Ren'Py Rhythm Game! Choose a song you'd like to play."

    # define the song titles and their files
    python:
        import os
        audio_directory = 'audio'
        audio_map = {
            'Night in the Woods - Die Anywhere Else': os.path.join(audio_directory, 'nitw_die_anywhere_else.mp3'),
            'Night in the Woods - Possum Springs': os.path.join(audio_directory, 'nitw_possum_springs.mp3'),
            'OMORI - Duet': os.path.join(audio_directory, 'omori_duet.mp3'),
            'OMORI - White Space': os.path.join(audio_directory, 'omori_white_space.mp3'),
            'Deltarune - Chill Buster': os.path.join(audio_directory, 'deltarune_chill_buster.mp3'),
            'Doki Doki Literature Club - Your Reality': os.path.join(audio_directory, 'ddlc_your_reality.mp3'),
            "Pokemon Dungeon - Dialga's Fight to the Finish": os.path.join(audio_directory, 'pokemon_dialga.mp3')
        }
        # use a menu
        choice = renpy.display_menu(list(audio_map.items()))

    # start the rhythm game
    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    call screen rhythm_game(choice)

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    $ hits = _return
    e "You hit [hits] notes. Good work!"

    return
