#!/usr/bin/env python3
"""
Convert Audacity label files to rhythm game beatmap format.

Usage:
    python audacity_to_beatmap.py labels.txt output_beatmap.txt
"""

import sys

def convert_audacity_to_beatmap(input_file, output_file):
    """Convert Audacity label file to beatmap format"""
    timestamps = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Audacity format: START\tEND\tLABEL
            parts = line.split('\t')
            if len(parts) >= 1:
                try:
                    timestamp = float(parts[0])
                    timestamps.append(timestamp)
                except ValueError:
                    continue
    
    # Sort timestamps (just in case)
    timestamps.sort()
    
    # Write to beatmap file
    with open(output_file, 'w') as f:
        for timestamp in timestamps:
            f.write(f'{timestamp:.4f}\n')
    
    print(f'✓ Converted {len(timestamps)} labels from {input_file}')
    print(f'✓ Output saved to {output_file}')
    
    # Show some stats
    if len(timestamps) > 1:
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        bpm = 60.0 / avg_interval if avg_interval > 0 else 0
        print(f'  Average interval: {avg_interval:.3f}s')
        print(f'  Approximate BPM: {bpm:.1f}')
        print(f'  First beat: {timestamps[0]:.3f}s')
        print(f'  Last beat: {timestamps[-1]:.3f}s')

def main():
    if len(sys.argv) != 3:
        print('Usage: python audacity_to_beatmap.py input_labels.txt output_beatmap.txt')
        print('')
        print('Example:')
        print('  python audacity_to_beatmap.py labels.txt dae_song.beatmap.txt')
        print('')
        print('How to create labels in Audacity:')
        print('  1. Open your audio file in Audacity')
        print('  2. Press Space to play')
        print('  3. Press Ctrl+M (Cmd+M on Mac) on each beat while playing')
        print('  4. Press Enter to leave labels unnamed')
        print('  5. File → Export → Export Labels')
        print('  6. Run this script to convert to beatmap format')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        convert_audacity_to_beatmap(input_file, output_file)
    except FileNotFoundError:
        print(f'Error: File not found: {input_file}')
        print('Make sure the file exists in the current directory.')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()