define e = Character("Eileen")

label start:
    scene bg room
    e "Welcome to the Ren'Py Rhythm Game! Choose a song you'd like to play."

    # define the song titles and their files
    python:
        import os
        audio_map = {
            'Night in the Woods - Die Anywhere Else': (
                'audio/nitw_die_anywhere_else.mp3',
                'audio/nitw_die_anywhere_else.beatmap.txt'
                ),
            'Night in the Woods - Possum Springs': (
                'audio/nitw_possum_springs.mp3',
                'audio/nitw_possum_springs.beatmap.txt'
                ),
            'OMORI - Duet': (
                'audio/omori_duet.mp3',
                'audio/omori_duet.beatmap.txt'
                ),
            'OMORI - Stardust Diving': (
                'audio/omori_stardust_diving.mp3',
                'audio/omori_stardust_diving.beatmap.txt'
                ),
            'Deltarune - Chill Buster': (
                'audio/deltarune_chill_buster.mp3',
                'audio/deltarune_chill_buster.beatmap.txt'
                ),
            'Doki Doki Literature Club - Your Reality': (
                'audio/ddlc_your_reality.mp3',
                'audio/ddlc_your_reality.beatmap.txt'
                ),
            "Pokemon Dungeon - Dialga's Fight to the Finish": (
                'audio/pokemon_dialga.mp3',
                'audio/pokemon_dialga.beatmap.txt'
                )
        }
        # use a menu
        choice = renpy.display_menu(list(audio_map.items()))

    # start the rhythm game
    # window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    # unpack the file paths associated with the chosen song
    $ audio_path, beatmap_path = choice
    call screen rhythm_game(audio_path, beatmap_path, beatmap_stride=2)

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    $ num_hits, num_notes = _return
    e "You hit [num_hits] notes out of [num_notes]. Good work!"

    return
