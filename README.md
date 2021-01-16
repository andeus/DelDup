# DelDup

Efface les fichiers identiques qui sont en plusieurs copies

Concu surtout pour unix, il fonctionne sur windows. Par contre, le  parametre --force ne sert pas fonctionne. 
Le fichier g3vLog est une librairie, il doit etre dans le pythonpath ou dans le meme repertoire que delDup.py.

Les parametres:
 --original indique les fichiers que tu veux conserver
 --copie indique les fichiers que tu veux effacer quand il en a trouvé une copie identique dans original
 --ablanc n'efface rien ne fait que te dire ce qu'il aurait effacé
 --force change les droits sur les fichiers pour les lire et les effacer, ne s'applique pas à windows

Le programme valide toujours que la copie et l'origiinal ne sont pas le même fichier physique. Ce qui permet de spécifier le même path pour original et copie. De cette maniere le programme eliminera tous les doublons que tu as. Seul inconvient, tu n'as pas le control sur le donblon eliminé.

Evidemment, le programme par l'arbre des repertoire, pas juste le repertoire courant.

Je n'ai pas vu de probleme quand original et copie sont differents.
Il plantait des fois quand ces 2 parametres sont identiques. Je me souviens pas si ca été fixé.

