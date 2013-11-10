cachedtexeq
===========

LaTeX equation to vector image. This is a Python script/module that allows to produce images from LaTeX equations. In particular it has been designed to manage a cache of expressions generated to speedup the process in certain conditions, and also to automatically convert the output to the required target.

Currently it supports PDF SVG and PNG by means of some external tools

Requirements:
- pdflatex with standalone and varwidth packages
- SVG requires the package pdf2svg
- PNG requires ImageMagick that provides convert utility 

Note: the conversion from PDF to SVG provided by ImageMagic does not work well

Tested under Ubuntu 13.04
