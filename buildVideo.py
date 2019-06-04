#!/usr/bin/env python

import json, math, os.path, shutil, subprocess, sys
from PIL import Image
from pydub import AudioSegment

FPS = 60
msPerFrame = 1000 / float(FPS)

def slide(a, b, direction, duration=250):
	frameDuration = int(round(duration / msPerFrame))
	if direction == 'right' or direction == 'down':
		a, b = b, a
	ai, bi = a[1], b[1]

	output = []
	for i in xrange(frameDuration):
		ratio = float(i + 1) / (frameDuration + 1)
		im = Image.new('RGBA', ai.size)
		output.append(im)
		if direction == 'left' or direction == 'right':
			x = int(round(ratio * ai.size[0]))
			if direction == 'left': x = ai.size[0] - x
			ab = (x - ai.size[0], 0)
			bb = (x, 0)
		elif direction == 'up' or direction == 'down':
			y = int(round(ratio * ai.size[1]))
			if direction == 'up': y = ai.size[1] - y
			ab = (0, y - ai.size[1])
			bb = (0, y)
		im.paste(ai, ab)
		im.paste(bi, bb)
	return output

def main():
	if not os.path.exists('combined.wav'):
		print 'No combined wav file'
		return 1

	try:
		shutil.rmtree('frames')
	except:
		pass
	os.makedirs('frames')

	transitionTimes = json.load(file('combined.tmap'))
	transitionFrames = [int(round(x / msPerFrame)) for x in transitionTimes]
	transitions = {}
	outroTransition = None

	combinedWav = AudioSegment.from_wav('combined.wav')
	totalFrameLength = int(math.ceil(len(combinedWav) / 1000.0 * FPS))

	slides = []
	for line in file('config'):
		line = line.strip()
		if not line: continue
		line = line.split(' ')
		if line[0] == 'slide':
			slideNum = int(line[1]) - 1
			r = 3
		elif line[0] == 'outro':
			slideNum = -1
			r = 2
		else:
			print 'Unknown slide command:', line
			return 1

		if line[r] == 'none':
			transition = None
		else:
			transition = []
			for x in line[r:]:
				try:
					transition.append(int(x))
				except:
					try:
						transition.append(float(x))
					except:
						transition.append(x)
		slides.append('slides/slide-%i.png' % slideNum if slideNum != -1 else 'outro.png')
		if slideNum == -1:
			outroTransition = transition
		elif slideNum > 0:
			transitions[slideNum - 1] = transition

	if outroTransition is not None:
		transitions[len(transitions)] = outroTransition

	ct = []
	for i in xrange(len(transitions)):
		ct.append(transitions[i])
	transitions = ct

	slides = [(fn, Image.open(fn)) for fn in slides]

	thumbnail = slides[0][1].copy()
	thumbnail.thumbnail((1280, 720))
	thumbnail.save('thumbnail.png')

	outFrames = [None] * totalFrameLength

	for i, transition in enumerate(transitions):
		print 'Building transition', i, transition
		print slides[i], slides[i + 1]
		if transition is not None:
			frames = slide(slides[i], slides[i + 1], *transition[1:])
			offset = transitionFrames[i] - len(frames) / 2
			for j, frame in enumerate(frames):
				outFrames[offset + j] = frame
		else:
			offset = transitionFrames[i]
		for j in xrange(offset):
			if outFrames[j] is None:
				outFrames[j] = i
	for i in xrange(totalFrameLength):
		if outFrames[i] is None:
			outFrames[i] = len(slides) - 1

	for i, frame in enumerate(outFrames):
		print '%i/%i' % (i + 1, len(outFrames))
		fn = 'frames/%06i.png' % i
		if isinstance(frame, int):
			os.symlink(os.path.abspath(slides[frame][0]), fn)
		else:
			frame.save(fn)

	print 'Encoding video'
	subprocess.check_output(['ffmpeg', '-r', str(FPS), '-f', 'image2', '-s', '3840x2160', '-i', 'frames/%06d.png', '-i', 'combined.wav', '-vcodec', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', '-acodec', 'aac', '-b:a', '256k', 'rendered.mp4'])
	print 'DONE!'

if __name__=='__main__':
	sys.exit(main(*sys.argv[1:]))
