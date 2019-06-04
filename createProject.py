import glob, os, os.path, subprocess, sys

def main(proj=None, pdffn=None):
	if proj is None or pdffn is None:
		print 'Usage: createProject.py projectName slides.pdf'
		return 1

	os.makedirs(proj)
	os.makedirs(proj + '/wavs')
	slidePath = proj + '/slides'
	os.makedirs(slidePath)
	os.symlink(os.path.abspath('buildVideo.py'), os.path.abspath(proj + '/buildVideo.py'))
	os.symlink(os.path.abspath('soundtool.py'), os.path.abspath(proj + '/soundtool.py'))
	print 'Created project directory at', proj
	print 'Converting PDF -- this will take a while'

	subprocess.call(['convert', '-density', '768', pdffn, '-resize', '50%', slidePath + '/slide.png'])
	print 'Creating project config'

	maxSlide = max(*[int(fn.rsplit('-', 1)[1].split('.png', 1)[0]) for fn in glob.glob(slidePath + '/slide-*.png')])

	with file(proj + '/config', 'w') as fp:
		for i in xrange(maxSlide + 1):
			print >>fp, 'slide %i -- %s' % (i + 1, 'slide left' if i > 0 else 'none')

if __name__=='__main__':
	sys.exit(main(*sys.argv[1:]))
