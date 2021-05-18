# Ren'Py Rhythm: A Rhythm Game Engine for Ren'Py

**Play it now on [itch.io](https://r3dhummingbird.itch.io/renpy-rhythm-game) or watch a demo on [YouTube](https://youtu.be/7fMig9BmDzY)**

## About

**Ren'Py Rhythm** is a rhythm game engine built with the [Ren'Py](http://renpy.org/) Visual Novel Engine and [Aubio](https://aubio.org/), a libraray for audio labeling. Aubio is used to automatically generate beat map for any custom audio file.

You can use this project as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project, using any music you like and have the beat map automatically generated for you. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-rhythm#guide-for-integrating-into-a-renpy-project) below.

The music files in `game/audio` are for demonstration purpose only. The author of this repo has no right over them.

## Compatibility

This project is built with **Ren'Py SDK >= 7.4.0** and is also compatible with **Ren'Py SDK <= 7.3.5**.

## Gameplay Demo

Use the four arrow keys on your keyboard to play the game. 

<img src="https://github.com/RuolinZheng08/renpy-rhythm/blob/master/demo.gif" alt="Gameplay Example" width=600>

## Guide for Integrating into a Ren'Py Project

All of the files essential to the chess engine are in `game/00-renpythm`. Therefore, you only need to copy the entire `00-renpythm`directory into your Ren'Py `game` directory.

### Structure of `00-renpythm`

```
00-renpythm/
    - images                        # music note images
    - rhythm_game_displayable.rpy   # core GUI class
```

The core GUI class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `RhythmGameDisplayable` inside `rhythm_game_displayable.rpy`.

To call the rhythm game displayable screen, all you need is a audio file and its corresponding beat map text file. The utilities to automatically generate beat map files is included in `00-renpythm-utils` and the procedure is described below in details.

Take for example a file in `game/audio` named `my_music.mp3`. Its full path is `audio/my_music.mp3`  which you need to pass to the `rhythm_game` screen. (Also see the `game/script.rpy` file in this repo for more examples.)

```renpy
window hide
$ quick_menu = False

# avoid rolling back and losing chess game state
$ renpy.block_rollback()

call screen rhythm_game('audio/my_music.mp3', 'audio/my_music.beatmap.txt')

# avoid rolling back and entering the chess game again
$ renpy.block_rollback()

# restore rollback from this point on
$ renpy.checkpoint()

$ quick_menu = True
window show

$ num_hits, num_notes = _return
"You hit [num_hits] notes out of [num_notes]. Good work!"
```

### Automatic Generation of Beat Map Files

This project leverages the onset detection feature in [Aubio's Python module](https://github.com/aubio/aubio/tree/master/python) to automatically generate beat map for any audio file. The script to generate a beat map is `00-renpythm-utils/generate_beatmap.py`.

You will need to install Python to run this script. This script is developed using MacOS's default Python 2.7.16.

```bash
Usage: python generate_beatmap.py [input]
```

As an example, `python generate_beatmap.py audio/my_music.mp3` will generate `audio/my_music.beatmap.txt`.

The script can also be run on an entire directory, `python generate_beatmap.py audio/` will take all valid audio files and generate their beat maps.

`beatmap.txt` is really just a text file with floating point numbers separated by newlines, each denoting when a note should appear. It's usually a couple hundred lines long, meaning that the song has a couple hundred notes. It may look like below, where the first note appears `0.0259` second into the song and the last note shown appears `2.7948` seconds into the song.

```
0.0259
0.4201
0.8147
1.2137
1.6092
2.0036
2.3981
2.7948
```

### Manually Specifying a Beat Map

You may also manually create your beat map text file, as long as it adheres to the format shown above.

### Adjust Difficulty Levels

If you are looking for ways to implement different difficulty levels. The following variables may be of interes:

- `RhythmGameDisplayable.note_offset` which affects `RhythmGameDisplayable.note_speed` computed as `note_speed = config.screen_height / note_offset`. `note_offset` is the total time in seconds it takes for a note to scroll vertically across the screen. Hence, a smaller `note_offest` results in a larger `note_speed` - faster moving notes - and increases the game's difficulty.
- The `beatmap_stride` passed to the constructor of `RhythmGameDisplayable`. This must be a non-negative integer and defaults to 2. A smaller `beatmap_stride` like 1 will result in drastically more notes appearing on the screen, increasing the game's difficulty.

## Continuous Development and Contribution
The project is under active maintenance and development. Please feel free to submit a GitHub issue for bugs and feature requests. Please also feel free to contribute by submitting GitHub issues and PRs. 