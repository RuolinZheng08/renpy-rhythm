# Beatmap Creation Tools

Tools for creating and editing beatmaps using Audacity for visual/audio feedback.

## Why Use These Tools?

The original `generate_beatmap.py` creates beatmaps automatically using audio analysis, but manual creation in Audacity offers several advantages:

- **Visual feedback** - See the waveform while placing beats
- **Audio playback** - Tap beats in real-time with keyboard shortcuts
- **Easy editing** - Drag beats to adjust timing visually
- **More accurate** - Human timing often feels more natural for rhythm games
- **Creative control** - Place notes exactly where you want them

## Quick Start

### Method 1: Create Beatmap from Scratch

Perfect for complete creative control over note placement.

1. **Open your audio file in Audacity**
2. **Press Space to start playback**
3. **Press Ctrl+M** (Cmd+M on Mac) on each beat while the song plays
   - Labels are placed at the current playback position
   - Press Enter to leave labels unnamed (faster workflow)
4. **Review and adjust**
   - Zoom in (Ctrl+1) for precise placement
   - Drag labels to fine-tune timing
   - Delete unwanted labels with Delete key
5. **Export labels**: File → Export → Export Labels (save as `labels.txt`)
6. **Convert to beatmap format**:
```bash
python audacity_to_beatmap.py labels.txt my_song.beatmap.txt
```

### Method 2: Edit Auto-Generated Beatmap

Start with automatic detection, then refine manually.

1. **Generate initial beatmap**:
```bash
python ../00-renpy-rhythm-utils/generate_beatmap.py my_song.wav
```

2. **Convert to Audacity labels**:
```bash
python beatmap_to_audacity.py my_song.beatmap.txt my_song_labels.txt
```

3. **Edit in Audacity**:
   - Open your audio file in Audacity
   - File → Import → Labels (select `my_song_labels.txt`)
   - Adjust/add/remove beats visually
   - File → Export → Export Labels

4. **Convert back to beatmap**:
```bash
python audacity_to_beatmap.py my_song_labels_refined.txt my_song.beatmap.txt
```

## Files

- **`audacity_to_beatmap.py`** - Convert Audacity label files to beatmap format
- **`beatmap_to_audacity.py`** - Convert beatmap files to Audacity labels for editing

## Tips & Tricks

### Real-Time Label Placement
- **Use Ctrl+M while playing** - This places labels at the playback position, not where you click
- **Practice difficult sections** - Loop sections (Ctrl+L) to nail complex rhythms
- **Slow down fast songs** - Effect → Change Tempo at -25% makes it easier to tap accurately

### Visual Editing
- **Zoom in** (Ctrl+1) for frame-accurate placement
- **Use the spectrogram view** - View → Spectrogram - bass hits show clearly
- **Enable snap-to** - Helps align to grid for consistent spacing

### Workflow Optimization
- **Leave labels unnamed** - Just press Enter after Ctrl+M for faster workflow
- **Do multiple passes** - Rough placement first, then refine
- **Use a metronome** - Play along with an online metronome for consistent timing
- **Check your work** - Play through with labels visible to verify accuracy

## File Formats

### Audacity Label Format
```
0.5000	0.5000	
1.0000	1.0000	
1.5000	1.5000	
```
Three tab-separated columns: START, END, LABEL (point labels have same start/end)

### Beatmap Format
```
0.5000
1.0000
1.5000
```
One timestamp per line in seconds

## Requirements

- Python 3.6 or higher
- Audacity (free audio editor)
- No additional Python packages required for `audacity_to_beatmap.py` and `beatmap_to_audacity.py` (standard library only)
- `generate_beatmap.py` requires `aubio` (`pip install aubio`; see the main README if the build fails)

## Troubleshooting

**Q: Labels appear at my click position, not playback position**  
A: Use **Ctrl+M** while playing, not Ctrl+B. Ctrl+M places labels at playback position.

**Q: How do I adjust an existing label?**  
A: Click the label marker and drag it left/right along the timeline.

**Q: Can I use this with the automatic beatmap generator?**  
A: Yes! Generate an initial beatmap with `generate_beatmap.py`, convert it to labels with `beatmap_to_audacity.py`, refine in Audacity, then convert back with `audacity_to_beatmap.py`.

**Q: My beatmap has too many/few notes**  
A: Adjust the `beatmap_stride` parameter in your Song definition, or create a custom beatmap with exactly the notes you want.

## License

Same as the parent project (MIT License)