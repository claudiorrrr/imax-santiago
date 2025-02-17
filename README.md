El otro día estaba pensando en lo horribles que son las páginas de los cines. Difíciles de leer, de comprar, etc. Y voy poco al cine. Y, cuando voy, me gusta ver en IMAX. Y encontrar películas en IMAX en estas páginas tan feas y difíciles se me hacía cuesta arriba. Así que hice un script que me ayude a listar todas las películas que actualmente están en cartelera en IMAX. Y este es el script. 

## Instalación

Para instalarlo, recomiendo correrlo dentro de un `virtualenv` en Python 3.10. 

```
python3.10 -m virtualenv venv
source venv/bin/activate
python install -r requirements.txt
python3 check-movies-json.py
```

Puedes ver qué películas en IMAX Plaza Egaña están hoy en exhibición acá https://claudiorrrr.github.io/imax-santiago/

## To-Do:

- [ ] Resolver scrapping de [Cinemark](https://www.cinemark.cl/cine?tag=511&cine=cinemark_mallplaza_vespucio)
- [ ] Mejorar diseño?