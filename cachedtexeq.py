#
# Cached LaTeX equation to Image/Vector
#
# Creating images from equation just requires something as: pdflatex "\def\formula{$1}\input{formula.tex}"
# but in this case we need to manage multiple equations as single images.
#
# This is similar to functionalities present in LaTeX to HTML tools found around, 
# this is provided both as a script and as a module to be incorportated in other application (e.g. pydot)
#
# Author:
# Emanuele Ruffaldi <emanuele.ruffaldi@gmail.com>
#
# Initial 2013/11/10 - version 1.0
#
# Licensed as BSD
#
# -----------------------------------------
# Requires:
# - pdflatex with standalone and varwidth packages
# - pdf2svg for producing svg images 
# - convert utility from ImageMagick for converting to png
#
# Future/TODO:
# - better cleanup of cached images

import sys,subprocess, base64,argparse,os,shutil

validformats = set(["pdf","svg","png"])

formula="""\\documentclass[crop=true,border=0pt]{standalone}
\\usepackage{amsmath}
\\usepackage{varwidth}
\\begin{document}
\\begin{varwidth}{\\linewidth}
\\[ \\formula \\]
\\end{varwidth}
\\end{document}"""

def clearcache(cd=None):
	"""clears the cache directory specified or the default one"""
	cd = os.environ.get("CACHEDEQ","cachedeq.dir")
	if not os.path.isdir(cd):
		return True
	cdm = os.path.join(cd,".cachedeq")
	if not os.path.isfile(cdm):
		return False
	else:
		shutil.rmtree(cd)
		return True

def getequation(expression,cd=None,invalidate=False,format="pdf",showerror=False):
	if format not in validformats:
		return (False,"not a valid format:"+str(validformats))
	if cd is None:
		cd = os.environ.get("CACHEDEQ","cachedeq.dir")
	cdm = os.path.join(cd,".cachedeq")
	if not os.path.isdir(cd):
		os.mkdir(cd)
	if not os.path.isfile(cdm):
		x = open(cdm,"w");
		x.close()
	if not os.path.isfile(cdm):
		return (False,"cannot create files in cache dir "+cd)

	ce = base64.b64encode(expression)
	fce = os.path.join(cd,ce)

	ftex = fce + ".tex"
	fpdf = fce + ".pdf"
	fout = fce + "." + format
	
	# texfile -> pdf -> outputs	
	if invalidate or not os.path.isfile(ftex):
		# TODO: clear all below
		if os.path.isfile(fpdf):
			os.unlink(fpdf)
		o = open(ftex,"w")
		o.write("\\def\\formula{"+expression+"}\n" + formula)
		o.close()
	if invalidate or not os.path.isfile(fpdf):
		# TODO: clear all below, not just current fout
		if os.path.isfile(fout):
			os.unlink(fout)
		if not showerror:
			x = subprocess.PIPE
		else:
			x = None
		subprocess.call(["pdflatex","-interaction","nonstopmode","-output-directory="+cd,ftex],stdout=x,stderr=x)
		if not os.path.isfile(fpdf):
			return (False,"cannot create file. Error in latex:"+ftex)
		else:
			for x in [".aux",".log"]:
				fx = fce + x
				if os.path.isfile(fx):
					os.unlink(fx)
	if fpdf != fout:
		if invalidate or not os.path.isfile(fout):
			if format == "svg":
				subprocess.call(["pdf2svg",fpdf,fout])
			elif format == "png":
				subprocess.call(["convert","-density","300",fpdf,"-quality","90",fout])
			if not os.path.isfile(fout):
				return (False, "cannot convert file "+fpdf+" to "+fout)
	return (True,fout)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Cached Latex equation')
	parser.add_argument('expression',nargs="?",help="latex expression")
	parser.add_argument('--format',default="pdf",help="output format: pdf or svg or png")
	parser.add_argument('--output',help="output filename")
	parser.add_argument('--invalidate',action="store_true",default=False,help="invalidate cached")
	parser.add_argument('--cachedir',help="cache folder. Default is ")
	parser.add_argument('--clear',action="store_true",help="clear cache")
	parser.add_argument('--showerror',action="store_true",help="show latex error")

	args = parser.parse_args()

	cd = args.cachedir

	if args.clear:
		if not clearcache(cd):
			print "cannot clear cache"
			sys.exit(-2)
		else:
			print "cleaned"
			sys.exit(0)
	elif args.expression is None:
		print "missing expression"
		args.help()
		sys.exit(-2)

	ok,what = getequation(args.expression,cd=cd,invalidate=args.invalidate,showerror=args.showerror,format=args.format)

	if not ok:
		print what
		sys.exit(-1)
	else:
		ro = what
	if args.output is not None:
		shutil.copyfile(ro,args.output)
		ro = args.output	
	print ro