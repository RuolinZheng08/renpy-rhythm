# Ren'Py Rhythm: A Rhythm Game Engine for Ren'Py

**Play it now on [itch.io](https://r3dhummingbird.itch.io/renpy-rhythm-game) or watch a demo on [YouTube](https://youtu.be/7fMig9BmDzY)**

## About

**Ren'Py Rhythm** is a rhythm game engine built with the [Ren'Py](http://renpy.org/) Visual Novel Engine and [Aubio](https://aubio.org/), a libraray for audio labeling. Aubio is used to automatically generate beat map for any custom audio file.

You can use this project as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project, using any music you like and have the beat map automatically generated for you. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-rhythm#guide-for-integrating-into-a-renpy-project) below.

## Compatibility

This project is compatible with both **Ren'Py 7** and **Ren'Py 8**.

## Gameplay Demo

Use the four arrow keys on your keyboard to play the game. A `Good` hit scores 60, and a `Perfect` hit scores 100. Hitting the note too early results in a `Miss`.

<img src="https://github.com/RuolinZheng08/renpy-rhythm/blob/master/demo.gif" alt="Gameplay Example" width=600>

The game also supports a high-score system stored in Ren'Py's `persistent` object store.

<img src="https://github.com/RuolinZheng08/renpy-rhythm/blob/master/high_score.gif" alt="High Score System" width=600>

## Guide for Integrating into a Ren'Py Project

All of the files essential to the engine are in `game/00-renpy-rhythm`. Therefore, you only need to copy the entire `00-renpy-rhythm`directory into your Ren'Py `game` directory.

### Structure of `00-renpy-rhythm`

```
00-renpy-rhythm/
    - images                        # music note images
    - rhythm_game_displayable.rpy   # core GUI class
```

The core GUI class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `RhythmGameDisplayable` inside `rhythm_game_displayable.rpy`.

To call the rhythm game displayable screen, all you need is a audio file and its corresponding beat map text file. The utilities to automatically generate beat map files is included in `00-renpy-rhythm-utils` and the procedure is [described below in details](https://github.com/RuolinZheng08/renpy-rhythm#automatic-generation-of-beat-map-files).

Take for example a file in `game/audio` named `my_music.mp3`. Its full path is `audio/my_music.mp3`  which you need to pass to the `rhythm_game` screen. (Also see the `game/script.rpy` file in this repo for more examples.)

See below for a simple example. See `script.rpy` and the `rhythm_game_entry_label` in `rhythm_game_displayable.rpy` for a more in-depth example.

```renpy
window hide
$ quick_menu = False

# avoid rolling back and losing chess game state
$ renpy.block_rollback()

$ song = Song('My Music Title', 'audio/my_music.mp3', 'audio/my_music.beatmap.txt', beatmap_stride=2)
$ rhythm_game_displayable = RhythmGameDisplayable(song)
call screen rhythm_game(rhythm_game_displayable)

# avoid rolling back and entering the chess game again
$ renpy.block_rollback()

# restore rollback from this point on
$ renpy.checkpoint()

$ quick_menu = True
window show
```

### Automatic Generation of Beat Map Files

This project leverages the onset detection feature in [Aubio's Python module](https://github.com/aubio/aubio/tree/master/python) to automatically generate beat map for any audio file. The script to generate a beat map is `00-renpy-rhythm-utils/generate_beatmap.py`.

**You will need to have Python to run this script** instead of using the Python provided by Ren'Py. This script is developed using MacOS's default Python 2.7.16.

```bash
Usage: python generate_beatmap.py [input]
```

As an example, `python generate_beatmap.py audio/my_music.mp3` will generate `audio/my_music.beatmap.txt`.

The script can also be run on an entire directory, `python generate_beatmap.py audio/` will take all valid audio files and generate their beat maps.

`beatmap.txt` is really just a text file with floating point numbers separated by newlines, each denoting when a note should appear. It's usually a couple hundred lines long, meaning that the song has a couple hundred notes. It may look like below, where the first note appears `0.0259` second into the song and the last note shown appears `2.7948` seconds into the song. See those `game/audio/*.beatmap.txt` for more information.

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

If you are looking for ways to implement different difficulty levels. The following variables may be of interest:

- `RhythmGameDisplayable.note_offset` which affects `RhythmGameDisplayable.note_speed` computed as `note_speed = config.screen_height / note_offset`. `note_offset` is the total time in seconds it takes for a note to scroll vertically across the screen. Hence, a smaller `note_offest` results in a larger `note_speed` - faster moving notes - and increases the game's difficulty.
- The `beatmap_stride` passed to the constructor of `RhythmGameDisplayable`. This must be a non-negative integer and defaults to 2. A smaller `beatmap_stride` like 1 will result in drastically more notes appearing on the screen, increasing the game's difficulty.

## Continuous Development and Contribution
The project is under active maintenance and development. Please feel free to submit a GitHub issue for bugs and feature requests. Please also feel free to contribute by submitting GitHub issues and PRs. 

## Music File Credit

All music files are copyright free ones found on SoundCloud.

- [Positivity](https://soundcloud.com/nocopyrightlofi/no-copyright-chill-lofi-hiphop-positivity-by-envy)
- [Isolation](https://soundcloud.com/nocopyrightlofi/no-copyright-chill-lofi-hiphop)
- [Thoughts](https://soundcloud.com/nocopyrightlofi/no-copyright-chill-lofi-hip)
- [Pearlescent](https://soundcloud.com/nocopyrightlofi/no-copyright-chill-lofi-hiphop-purlecent-by-matxete-prod)
