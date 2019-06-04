#!/usr/bin/env python

import glob, json, os, sys
from pydub import AudioSegment
from pydub.playback import play as _play

def createBase():
	if os.path.exists('soundconfig.json'):
		return
	files = [x[1] for x in sorted([(int(fn.rsplit('/', 1)[1].split('.', 1)[0]), fn) for fn in glob.glob('wavs/*.wav')], key=lambda x: x[0])]
	with file('soundconfig.json', 'w') as fp:
		json.dump(dict(
				files=files, 
				gaps=[1000] * (len(files) - 1), 
				transitions=[], 
				trimStart=[0] * len(files), 
				trimEnd=[0] * len(files), 
			), fp)

def play(seg):
	try:
		_play(seg)
	except KeyboardInterrupt:
		print

def main():
	def trimmed(i):
		wav = wavs[i]
		if trimEnd[i] != 0:
			return wav[trimStart[i]:-trimEnd[i]]
		return wav[trimStart[i]:].fade_in(200).fade_out(200)

	createBase()
	with file('soundconfig.json', 'r') as fp:
		config = json.load(fp)

	files = config['files']
	gaps = config['gaps']
	transitions = config['transitions']
	trimStart = config['trimStart']
	trimEnd = config['trimEnd']

	wavs = [AudioSegment.from_wav(fn) for fn in files]
	curGap = 0
	try:
		while True:
			try:
				line = raw_input('%sgap %i -- %i ms (%i/%i - %i/%i) > ' % (
					'*' if curGap in transitions else '', curGap, gaps[curGap], 
					trimStart[curGap], trimEnd[curGap], trimStart[curGap + 1], trimEnd[curGap + 1])).split(' ')
			except (KeyboardInterrupt, EOFError):
				break
			
			if len(line) == 0 or line[0] == '': continue
			cmd = line[0]
			if cmd == 'pb' or cmd == 'pa':
				play(trimmed(curGap if cmd == 'pb' else curGap + 1))
			elif cmd == 'p':
				a, b = trimmed(curGap), trimmed(curGap + 1)
				comb = a[-3500:].fade_in(200) + AudioSegment.silent(duration=gaps[curGap]) + b[:3500].fade_out(200)
				play(comb)
			elif cmd == 'pw' or cmd == 'w':
				twav = map(trimmed, xrange(len(wavs)))
				comb = AudioSegment.silent(duration=0)
				tmap = []
				time = 0
				for i, wav in enumerate(twav):
					comb += wav
					time += len(wav)
					if i < len(gaps):
						comb += AudioSegment.silent(duration=gaps[i])
						temp = time
						time += gaps[i] / 2
						if i in transitions:
							tmap.append(time)
						time = temp + gaps[i]
				if cmd == 'pw':
					play(comb)
				else:
					comb.export('combined.wav', format='wav')
					with file('combined.tmap', 'w') as fp:
						json.dump(tmap, fp)
			elif cmd == 'g':
				gaps[curGap] = int(line[1])
			elif cmd == 'ig':
				gaps[curGap] += 100
			elif cmd == 'dg':
				gaps[curGap] -= 100
			elif cmd == 't':
				if curGap in transitions:
					transitions = [x for x in transitions if x != curGap]
				else:
					transitions.append(curGap)
			elif cmd == 'f':
				if curGap < len(gaps) - 1:
					curGap += 1
				else:
					print 'Reached end'
			elif cmd == 'b':
				if curGap > 0:
					curGap -= 1
				else:
					print 'Reached start'
			elif cmd == 'tsb':
				trimStart[curGap] = int(line[1])
			elif cmd == 'teb':
				trimEnd[curGap] = int(line[1])
			elif cmd == 'tsa':
				trimStart[curGap + 1] = int(line[1])
			elif cmd == 'tea':
				trimEnd[curGap + 1] = int(line[1])
			else:
				print 'Unknown command:', cmd
	except:
		import traceback
		traceback.print_exc()

	print
	print 'Saving...',
	with file('soundconfig.json', 'w') as fp:
		json.dump(dict(files=files, gaps=gaps, transitions=transitions, trimStart=trimStart, trimEnd=trimEnd), fp)
	print 'Saved!'

if __name__=='__main__':
	sys.exit(main(*sys.argv[1:]))
