VideoTool101
============

I've been producing educational videos for many years now and one thing is always true: it takes a long damn time and a bunch of separate tools.  This is my attempt to fix both of those things.  This is an (almost) all-in-one suite for producing educational content in the slides + voiceover style.

Components
----------

- Project creation
- PDF to image conversion
- Audio stitching and editing
- Slide transitions
- Video compositing/rendering
- Thumbnail creation

Workflow
--------

1. Create your slide deck and export to PDF (I use Google Slides)
2. Record your audio using a push-to-record app that produces individual wav files (I use [https://github.com/daeken/PTTRecorderWpf](https://github.com/daeken/PTTRecorderWpf))
3. Run `./createProject.py ProjectName path/to/slides.pdf`
4. Copy wav files into `ProjectName/wavs`
5. From the project directory, run `./soundtool.py`
6. Set gap lengths/trimming for each audio sample and assign transition gaps
7. Export the audio track
8. (Optionally) Copy your endscreen to the project directory as `outro.png`
9. Set transition styles for each slide
10. From the project directory, run `./buildVideo.py`
11. Wait a couple hours for the video to encode
12. Upload `ProjectName/rendered.mp4` to YouTube

SoundTool Controls
------------------

SoundTool works around the concept of gaps -- you aren't assigning properties on individual sounds, but on the gaps between them.

- `g [length in ms]` -- Set the current gap length
- `ig` -- Adds 100ms to the current gap length
- `dg` -- Subtracts 100ms from the current gap length 
- `p` -- Plays the current gap (the last 3.5 seconds of the previous clip and first 3.5 seconds of the next clip, with whatever silence goes in between)
- `pb` -- Play the previous clip
- `pa` -- Play the following clip
- `pw` -- Play the entire audio track
- `t` -- Indicates that the current gap is a transition between slides (toggles on/off -- `*` at the start of the prompt tells you that it's currently marked as a transition)
- `f` -- Goes to the next gap
- `b` -- Goes to the previous gap
- `tsb [length in ms]` -- Sets the amount of time to trim from the start of the previous clip
- `teb [length in ms]` -- Sets the trim for the end of the previous clip
- `tsa [length in ms]` -- Sets the trim for the start of the next clip
- `tea [length in ms]` -- Sets the trim for the end of the next clip
- `w` -- Exports the audio track for consumption by buildVideo

All of your settings will be autosaved when you exit the tool, which you can do with ctrl-C or ctrl-D.

BuildVideo Controls
-------------------

The only controls for the building of videos happen in `config` in the project directory.  This is an index of slides and their transitions.  Here's an example showing a few key things:

```
slide 1 -- none
slide 2 -- slide up
slide 3 -- slide left
slide 4 -- slide left
slide 5 -- none
slide 6 -- slide left
slide 7 -- none
slide 8 -- slide left
slide 9 -- slide left
slide 10 -- slide left
slide 11 -- slide left
slide 12 -- slide left
slide 13 -- none
slide 14 -- none
slide 15 -- slide up
slide 16 -- slide left
slide 17 -- slide left
slide 18 -- slide left
slide 19 -- slide up
slide 20 -- slide left
slide 21 -- slide left 1000
slide 22 -- slide left
slide 23 -- slide left
slide 24 -- slide left
slide 25 -- slide left
slide 26 -- slide left
outro -- slide up
```

If you've added an endscreen (`outro.png`) you **must** add the outro line yourself, with whatever transition you want.  If you put a duration after a transition, you're telling it how long the transition should last in milliseconds; the default is 250ms.

Known Issues
------------

- Encoding the video is ungodly slow; a 12.5 minute video took more than 2 hours to encode on my very powerful laptop.  We likely can decrease the quality on the x264 encode.
- Your slides will be rendered to 3840x2160 (4k) and videos are locked to 60fps.
- You manually have to make your endscreen 3840x2160; any other size will fail, and no scaling is automatically done.
- Conversion from PDF to images takes **forever**.  We can parallelize this.
- This toolkit should include a Push-to-Record app.
