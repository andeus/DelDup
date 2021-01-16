import argparse
import sys
import logging
import os
import time

def var():
	debut=None
	maxRc=None	

logger = logging.getLogger("G3V")


def init(parser):
	parser.add_argument("--log_niveau",action='store',default='INFO',choices=['INFO','DEBUG','WARNING','ERROR'])
	parser.add_argument("--log_fichier",action='store',help="Indique dans quel fichier on doit envoyer le log")

def traiteArgs(args):
	fichier = args.log_fichier
	var.debut=time.time()
	var.maxRc=0
	log_dte_format = '%Y-%m-%d %H:%M:%S'
	log_format = '%(asctime)s {} %(process)d %(levelname).1s %(message)s'
	pgm = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	if fichier is not None:
		logging.basicConfig(filename=fichier,level=args.log_niveau,datefmt=log_dte_format,format=log_format.format(pgm))
	else:
		logging.basicConfig(level=args.log_niveau,datefmt=log_dte_format,format=log_format.format(pgm))
	parm = " ".join(sys.argv)
	logging.info("Demarre %s" % parm)

def setRc(rc):
	if rc > var.maxRc:
		varRc = rc

def exitRc(rc=0):
	setRc(rc)
	fin = time.time()
	duree = int((fin - var.debut) * 100) / 100.0
	cent = int((duree - int(duree))*100)
	duree = int(duree)
	sec = duree % 60
	duree = duree / 60
	min = duree % 60
	duree = duree / 60
	heure = duree % 24
	jour = duree / 24
	logger.info("Terminé rc %d Durée %d-%02d:%02d:%02d.%02d" % (rc,jour,heure,min,sec,cent))
	sys.exit(rc)
