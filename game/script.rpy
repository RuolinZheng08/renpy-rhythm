define e = Character("Eileen")

# define the song titles and their files
init python:
    # must be persistent to be able to record the scores
    songs = [
    Song('Isolation', 'audio/Isolation.mp3', 'audio/Isolation.beatmap.txt'),
    Song('Positivity', 'audio/Positivity.mp3', 'audio/Positivity.beatmap.txt'),
    Song('Pearlescent', 'audio/Pearlescent.mp3', 'audio/Pearlescent.beatmap.txt'),
    Song('Thoughts', 'audio/Thoughts.mp3', 'audio/Thoughts.beatmap.txt')
    ]

# map song name to high scores
default persistent.rhythm_game_high_scores = {
    song.name: (0, 0) for song in songs
}

# the song that the player chooses to play, set in `choose_song_screen` below
default selected_song = None

label start:
    scene bg room

    e "Welcome to the Ren'Py Rhythm Game! Choose a lofi song you'd like to play."

    call screen choose_song_screen(songs)
    $ selected_song = _return

    # avoid rolling back and losing game state
    $ renpy.block_rollback()

    # disable Esc key menu to prevent the player from saving the game
    $ _game_menu_screen = None

    call screen rhythm_game(selected_song)
    $ new_score = _return

    python:
        # XXX: old_percent is not used, but doing `old_score, _` causes pickling error
        old_score, old_percent = persistent.rhythm_game_high_scores[selected_song.name]
        if new_score > old_score:
            renpy.notify('New high score!')
            # compute new percent
            new_percent = selected_song.compute_percent(new_score)
            persistent.rhythm_game_high_scores[selected_song.name] = (new_score, new_percent)

    # re-enable the Esc key menu
    $ _game_menu_screen = 'save'

    # avoid rolling back and entering the game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    e "Nice work hitting those notes! Hope you enjoyed the game."

    return