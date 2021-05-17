# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

screen choose_song():
    add Solid('#000')

label start:
    scene bg room
    e "Welcome to the Ren'Py Rhythm Game! Choose a song you'd like to play."

    # start the rhythm game
    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    $ f = 'audio/small.mp3'
    call screen rhythm_game(f)

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    $ hits = _return
    e "You hit [hits] notes. Good work!"

    return
