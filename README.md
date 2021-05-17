# Renpythm: A Rhythm Game Engine for Ren'Py

**Play it now on [itch.io](https://r3dhummingbird.itch.io/renpy-rhythm-game)**

## About

**Renpythm** (combining the words Ren'Py and rhythm) is a rhythm game engine built with the [Ren'Py](http://renpy.org/) Visual Novel Engine and [Aubio](https://aubio.org/), a libraray for audio labeling. Aubio is used to automatically generate beat map for any custom audio file.

You can use this project as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project, using any music you like and have the beat map automatically generated for you. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-rhythm#guide-for-integrating-into-a-renpy-project) below.

The music files in `game/audio` are for demonstration purpose only. The author of this repo has no right over them.

## Compatibility

This project is built with **Ren'Py SDK >= 7.4.0** and has not been tested on **Ren'Py SDK <= 7.3.5**.

## Gameplay Demo

Use the four arrow keys on your keyboard to play the game. 

<img src="https://github.com/RuolinZheng08/renpy-rhythm/blob/master/demo.gif" alt="Gameplay Example" width=600>

## Automatic Generation of Beat Map for Any Song

This project leverages the onset detection feature in [Aubio's Python module](https://github.com/aubio/aubio/tree/master/python) to automatically generate beat map for any audio file. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-rhythm#guide-for-integrating-into-a-renpy-project) below if you'd like to manually specify the beat map.

## Guide for Integrating into a Ren'Py Project

All of the files essential to the chess engine are in `game/00-renpythm`. Therefore, you only need to copy the entire `00-renpythm`directory into your Ren'Py `game` directory.

### Structure of `00-renpythm`

```
00-renpythm/
    - images                        # music note images
    - python-packages               # Python libraries
    - rhythm_game_displayable.rpy   # core GUI class
```

The core GUI class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `RhythmGameDisplayable` inside `00-renpythm/rhythm_game_displayable.rpy`.

To call the rhythm game displayable screen, all you need is a file name, for example, a file in `game/audio` named `my_music.mp3`. Its full path is `audio/my_music.mp3`, which you need to pass to the `rhythm_game` screen. (Also see the `game/script.rpy` file in this repo for more examples.)

```renpy
window hide
$ quick_menu = False

# avoid rolling back and losing chess game state
$ renpy.block_rollback()

call screen rhythm_game('audio/my_music.mp3')

# avoid rolling back and entering the chess game again
$ renpy.block_rollback()

# restore rollback from this point on
$ renpy.checkpoint()

$ quick_menu = True
window show

$ num_hits, num_notes = _return
"You hit [num_hits] notes out of [num_notes]. Good work!"
```

### Manually Specifying a Beat Map

The automatically generated beat map is stored as a list of timestamps in seconds in `RhythmGameDisplayable.onset_times`. You may overwrite this list with your own list of timestamps, and make adjustment to some other `RhythmGameDisplayable` class attributes that depend on `RhythmGameDisplayable.onset_times`.

## Continuous Development and Contribution
The project is under active maintenance and development. Please feel free to submit a GitHub issue for bugs and feature requests. Please also feel free to contribute by submitting GitHub issues and PRs. 