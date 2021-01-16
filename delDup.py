#!/usr/bin/python3
import os
import sys
import argparse
from stat import *
import logging
import argparse
import hashlib

#import time

import g3vLog as gl

logger = logging.getLogger("G3V")



class fichier:
	
	BUF_SIZE = 4096
	rep = None
	nom = None
	htaille = None
	devide = None
	inode = None
	fullpath = None
	hdl = None
	detruit = False
	lienSymb = None
	md5 = {}
	
	def existe(self):
		return(os.access(self.fullpath,os.F_OK))
	
	def estLienSymb(self):
		return(self.lienSymb)
	
	def __init__(self,rep,nom,taille,device,inode,lienSymb):
		self.rep = rep
		self.nom = nom
		self.taille = taille
		self.device = device
		self.inode = inode
		self.lienSymb = lienSymb 
		self.fullpath = os.path.join(rep.racine,nom)

	def detruire(self,aBlanc,msg):
		self.detruit = True
		if aBlanc:
			logger.info("%s %s aurait été effacé" % (msg,self.fullpath))
		else:
			try:
				rc = os.remove(self.fullpath)
				logger.info("%s efface %s" % (msg,self.fullpath))
			except PermissionError:
				logger.warning("Incapable d'effacer %s" % (self.fullpath))
				
			
	def estDetruit(self):
		"""
		
		return 
			0 le fichier existe
			1 le fichier est detruit
			2 c'est un lien symbolique brise
		"""
		
		if self.detruit:
			return 1
		try:
			s = os.stat(self.fullpath)
			return 0 # si on est ici le fichier existe et si c'est un lien symbolique il est bon
		except FileNotFoundError:
			pass
		try:
			s = os.lstat(self.fullpath)
			return 2	# c'est un lien symbolique brisé
		except FileNotFoundError:
			self.detruit = False # il a été detruit et on ne le savait pass
			return 1
		
	def marqueDetruit(self):
		detruit = True
		
	def getTaille(self):
		return(self.taille)
		
	def getFullPath(self):
		return(self.fullpath)
		
	def ouvre(self):
		self.hdl = open(self.fullpath,"rb")
		self.noBlk = 0
		
	def lire(self):
		buffer = self.hdl.read(4096)
		if(self.noBlk == self.blkLu):
			self.md5.update(buffer)
			self.blkLu =+ 1
		self.noBlk =+ 1
		return(buffer)
		
	def getLINode(self,fichier):
		if fichier.device not in self.md5:
			self.md5[fichier.device] = {}
			
		if fichier.inode not in self.md5[fichier.device]:
			self.md5[fichier.device][fichier.inode] = []

		return(self.md5[fichier.device][fichier.inode])
		
	def compare(self,copie):
		"""
		
		retourne 
			0: different
			1: meme fichier
			2: identique
		"""
		
		lsrcMD5 = self.getLINode(self)
		lcopieMD5 = self.getLINode(copie)
		if id(lsrcMD5) == id(lcopieMD5):
			return(1)	# meme fichier
		nbBlkSrc = len(lsrcMD5)
		nbBlkCopie = len(lcopieMD5)
		maxBlk = min(nbBlkSrc, nbBlkCopie) # le maximum de blk que l'on peut verifier, c'est  le plus petit des 2
		if maxBlk > 0:
			if lsrcMD5[maxBlk-1] != lcopieMD5[maxBlk-1]:
				return(0)	# différent
#
# On doit finalement lire les fichiers
#
		md5_src	= hashlib.md5()
		md5_copie = hashlib.md5()
		with open(self.getFullPath(),"rb") as fsrc:
			with open(copie.getFullPath(),"rb") as fcopie:
				lu = 0
				for bufSrc in iter(lambda: fsrc.read(self.BUF_SIZE), b""):
					md5_src.update(bufSrc)
					if nbBlkSrc == lu:
						lsrcMD5.append(md5_src.digest())
						nbBlkSrc += 1
					bufCopie = fcopie.read(self.BUF_SIZE)
					md5_copie.update(bufCopie)
					if nbBlkCopie == lu:
						lcopieMD5.append(md5_copie.digest())
						nbBlkCopie += 1
#					if not lsrcMD5[lu] == lcopieMD5[lu]:
#						return[0] # diffrent, dans un with pas besoin de fermer
#
# On a pas de choix, faut comparer
#
					if not bufSrc == bufCopie:
						return(0)
		return(2) # identique
		

		
class special:

	nom = None
	mode = None
	
	def __init__(self,nom,mode):
	
		self.nom = nom
		self.mode = mode

class rep:
	lrep = None
	lfichier = None
	lspecial = None
	lsymb = None
	htaille = None
	racine = None
	
	def __init__(self,racine,force,phtaille=None):
	
		logger.info("Lecture rep: %s" % racine)
		self.lrep = []
		self.lfichier = []
		self.lspecial = []
		self.racine = racine
		
		if phtaille is None:
			self.htaille = {}
			htaille = self.htaille
		else:
			htaille = phtaille

		s = os.lstat(racine)
		if S_ISLNK(s.st_mode):
			self.lsymb = True
			logger.debug("   repoertoire lien symbolique")
		else:
			self.lsymb = False
			
		ignoreRep = False
		mode_chq = False
		if  not os.access(racine,os.X_OK):
			if force:
				try:
					s = os.stat(racine)
					mode = s.st_mode
					mode |= stat.S_IXUSR
					os.chmod(racine,mode)
					mode_chg = True
				except:
					ignoreRep = True
			else:
				ignoreRep = True

		if ignoreRep:
			logger.warning("Incapable de lire %s, ignoré" % racine)
			fic = fichier(self,"repertoire ilisible",-1000,0,0,True)
			self.lfichier.append(fic)
		else:
			for f in os.listdir(racine):
				if f in [".",".."]:
					continue
				nouvPath = os.path.join(racine,f)
				s = os.lstat(nouvPath)
				slien = S_ISLNK(s.st_mode)
				if slien:
					try:
						s = os.stat(nouvPath)
					except (FileNotFoundError,PermissionError):
						logger.warning("Lien symbolique %s invalide" % nouvPath)
						fic = fichier(self,f,-1,0,1,True) 
						self.lfichier.append(fic)

						taille = fic.getTaille()
						if taille not in htaille:
							htaille[taille] = []
						htaille[taille].append(fic)

						continue
						
				mode = s.st_mode
				if S_ISDIR(mode):
#					logger.info("Lecture rep: %s" % f)
					self.lrep.append(rep(nouvPath,force,htaille))
				elif S_ISREG(mode) | S_ISLNK(mode):
					logger.debug("Fichier: %s" % f)
					if not os.access(nouvPath,os.R_OK):
						if force:
							try:
								mode |= 256
								os.chmod(nouvPath,mode)
								fic = fichier(self,f,s.st_size,s.st_dev,s.st_ino,slien)
							except PermissionError:
								logger.warning("Incapable de lire %s" % nouvPath)
								fic = fichier(self,f,-1000,0,2,slien)
						else:
								logger.warning("Incapable de lire %s" % nouvPath)
								fic = fichier(self,f,-1000,0,2,slien)
					else:
						fic = fichier(self,f,s.st_size,s.st_dev,s.st_ino,slien)
					self.lfichier.append(fic)

					taille = fic.getTaille()
					if taille not in htaille:
						htaille[taille] = []
					htaille[taille].append(fic)

				else:
					logger.warning("Fichier special ignoré: %s" % f)
					self.lspecial.append(special(nouvPath,mode))
	
	def listTaille(self):

		return(self.htaille)
	
	def listFichier(self,taille):
		if taille not in self.htaille:
			return []
		return(self.htaille[taille])
		
	def delRepVide(self,aBlanc):
		
		if self.lsymb:
			return True;
		
		toutVide = True
		for rep in self.lrep:
			vide = rep.delRepVide(aBlanc)
			if not rep.lsymb:
				if vide:
					if aBlanc:
						logger.info("Rep %s aurait été détruit" % rep.racine)
					else:
						logger.info("Rep %s détruit" % rep.racine)
						os.rmdir(rep.racine)
				else:
					logger.debug("Rep %s PAS détruit" % rep.racine)
					toutVide = False
		if not toutVide:
			logger.debug("Rep %s PAS détruit, reste des enfants" % self.racine)
			return False
		
		if len(self.lspecial) > 0:
			logger.debug("Rep %s PAS détruit, reste fichiers speciaux" % self.racine)
			return False
			
		for fichier in self.lfichier:
			if not fichier.estDetruit():
				logger.debug("Rep %s PAS détruit, reste des fichiers" % self.racine)
				return False
		return True
	
	def marqueDetruit(self):
		
		for rep in self.lrep:
			logger.debug("Ignore %s" % rep.racine)
			rep.marqueDetruit()

		for fichier in self.lfichier:
			logger.debug("Ignore %s" % fichier.getFullPath())
			fichier.marqueDetruit()
	
	def delLienSymb(self,aBlanc):


		if self.lsymb:
			logger.debug("%s lien symbolique" % self.racine)
			self.marqueDetruit()
			if aBlanc:
				logger.info("%s aurait été effacé" % self.racine)
			else:
				rc = os.remove(self.racine)
				logger.info("Efface %s" % (self.racine))
			return
		
		for rep in self.lrep:
			rep.delLienSymb(aBlanc)
		for fichier in self.lfichier:
			if fichier.estLienSymb():
				fichier.detruire(aBlanc,"lien symbolique")
		
def valideRep(nom,rep):

	try:
			s = os.stat(rep)
			mode = s.st_mode
			if not S_ISDIR(mode):
				logger.error("La valeur [%s] du paramètre %s n'est pas un répertoire",rep,nom)
				exit(1)
	except OSError:
				logger.error("Le répertoire [%s] du paramètre %s n'est pas accessible",rep,nom)
				exit(2)

def efface(fichier,force):
	try:
		os.remove(fichier)
	except PermissionError:
		if force:
			rep = os.dirname(fichier)
			s = os.stat(rep)
			mode = s.st_mode
			mode |= stat.S_IWUSR
			try:
				os.chmod(rep,mode)
				logger.Warning("Changer les droits sur %s" % rep)
			except PermissionError:
				logger.Warning("Incapable d'effacer %s" % fichier)
				return(False)
			os.remove(fichier)
		else:
			logger.Warning("Incapable d'effacer %s" % fichier)
			return(False)
		return(True)
			
def init():

	parser = argparse.ArgumentParser(allow_abbrev=True)
	parser.add_argument("--original",action='store',required=True,help="répertoire contenant les fichiers originaux à conserver")
	parser.add_argument("--copie",action='store',required=True,help="répertoire contenant les fichiers en double à détruire")
	parser.add_argument("--aBlanc",action='store_true',help="Juste un rapport, n'efface pas les fichiers")
	parser.add_argument("--force",action='store_true',help="Essaie de changer temporairement les droits sur les fichiers pour lire ou effacer ceux-ci")

	gl.init(parser)
	
	args = parser.parse_args()
	gl.traiteArgs(args)

	src=args.original
	logger.info("Paramètre original: %s",src)
	valideRep("original",src)
	copie=args.copie
	logger.info("Paramètre copie: %s",copie)
	valideRep("original",src)
	aBlanc=args.aBlanc
	logger.info("Paramètre aBlanc: %s",aBlanc)
	force=args.force
	logger.info("Paramètre force: %s",force)

	return(src,copie,aBlanc,force)
	

def main():
	(src,copie,aBlanc,force) = init()
	srcRep = rep(src,force)
	copieRep = rep(copie,force)
	
	logger.info("detruit liens symboliques")
	copieRep.delLienSymb(aBlanc)
	
	logger.info("detruit fichiers vides")
	for ficCopie in copieRep.listFichier(0):
		if not ficCopie.estDetruit():
			ficCopie.detruire(aBlanc,"fichier vide")
		
	logger.info("detruit fichiers identiques")
	for taille in srcRep.listTaille():
		logger.debug("Examine fichiers taille %s" % taille)
		if taille > 0:
			for ficSrc in srcRep.listFichier(taille):
				if not ficSrc.estDetruit():
					logger.debug("fichier source %s" % ficSrc.getFullPath())
					srcLoggue = False
					for ficCopie in copieRep.listFichier(taille):
						logger.debug("   copie %s" % ficCopie.getFullPath())
						detruit = ficCopie.estDetruit()
						if detruit == 0:
							if ficCopie.existe():
								rc = ficSrc.compare(ficCopie)
##								logger.debug("rc compare: %d" % rc )
								if rc == 0:
									logger.debug("      fichier different")
								if rc == 1:
									logger.debug("      Meme fichier")
								if rc == 2:
									if not srcLoggue:
										logger.info("original:%s (%d)" % (ficSrc.getFullPath(),taille))
										srcLoggue = True
									logger.debug("      fichier identique")
									ficCopie.detruire(aBlanc,"    copie")
						elif detruit == 2:
							ficCopie.detruire(aBlanc,"lien symbolique brisé")
						else:
							logger.debug("      deja detruit")

	logger.info("detruit répertoires vides")
	copieRep.delRepVide(aBlanc)
				
	
if __name__ == "__main__":

	main()
	gl.exitRc()

		
