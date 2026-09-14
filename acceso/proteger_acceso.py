# -*- coding: utf-8 -*-
"""
GUARDIA DE LA PANTALLA DE ACCESO
=================================
Corre DENTRO de GitHub (no en una computadora nuestra) cada vez que alguien
publica un index.html. Si el que subieron no tiene los accesos reales, lo
reescribe con los correctos y lo vuelve a comitear.

Por que existe: el index.html lo regenera cada copia del proyecto a partir de
SU PROPIA tabla de PINs. Una copia de desarrollo, con los PINs de ejemplo,
publica un login de 3 accesos y deja al equipo entero afuera. Ya paso el
18/08 y el 11/09 de 2026.

Los candados que viven en los scripts solo protegen a quien tiene los scripts
al dia. Este vive en el repositorio: protege pase lo que pase, corra quien
corra, con la version que sea.

Los hashes NO son secretos: ya viajan dentro del index.html publicado. Por eso
este archivo puede vivir en el repo sin exponer ningun PIN.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
INDEX = os.path.join(RAIZ, 'index.html')
HASHES = os.path.join(AQUI, 'pines_hashes.json')
PLANTILLA = os.path.join(AQUI, 'index_template.html')

def salir(msg, codigo=0):
    print(msg)
    sys.exit(codigo)

for f in (HASHES, PLANTILLA):
    if not os.path.exists(f):
        salir(f"No esta {os.path.basename(f)}: no puedo verificar nada.", 1)

with open(HASHES, encoding='utf-8') as f:
    d = json.load(f)
DESTINOS, SALT, ITER = d['destinos'], d['salt'], d['iteraciones']

if not os.path.exists(INDEX):
    print("No hay index.html publicado. Lo genero.")
    actual, crudo = '', b''
else:
    with open(INDEX, 'rb') as f:
        crudo = f.read()
    actual = crudo.decode('utf-8', 'replace')

# El index que genera Windows viene con CRLF. Si se reescribe con LF, la proxima
# publicacion desde Windows marca el archivo entero como modificado aunque no
# haya cambiado nada. Se respeta el final de linea que ya tenia.
FIN = '\r\n' if b'\r\n' in crudo else '\n'

faltan = [h for h in DESTINOS if h not in actual]

if not faltan:
    salir(f"OK: el index.html publicado tiene los {len(DESTINOS)} accesos reales.")

print(f"PROBLEMA: al index.html publicado le faltan {len(faltan)} de {len(DESTINOS)} accesos.")
print("Lo mas probable: se publico desde una copia con los PINs de ejemplo.")
print("Restaurando...")

with open(PLANTILLA, encoding='utf-8') as f:
    html = f.read()
html = (html.replace('__PIN_DESTINOS__', json.dumps(DESTINOS, ensure_ascii=False))
            .replace('__PIN_SALT__', SALT)
            .replace('__PIN_ITER__', str(ITER)))

if '__PIN_DESTINOS__' in html or '__PIN_SALT__' in html:
    salir("No pude completar la plantilla. No toco nada.", 1)

with open(INDEX, 'w', encoding='utf-8', newline=FIN) as f:
    f.write(html.replace('\r\n', '\n'))
print(f"Restaurado: el index.html vuelve a tener los {len(DESTINOS)} accesos.")
