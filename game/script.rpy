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

label start:
    scene bg room

    # see rhythm_game_displayable.rpy    
    show screen choose_song_screen(songs)

    e "Welcome to the Ren'Py Rhythm Game! Choose a lofi song you'd like to play."

    e "Nice work hitting those notes! Hope you enjoyed the game."