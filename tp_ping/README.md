# # TP N1: App Layer

Trabajo práctico de Introducción a los Sistemas Distribuidos (75.43) - FIUBA

2do. Cuatrimestre 2020  
  
**Integrantes:**  
- Capolupo, Mauro  
- Franco, Tomás  
- Impaglione, Rocío  
  
[Informe](https://www.overleaf.com/read/xnrvgdyxxmqj)


# Ejecucion

### Server

Para levantar el server basta con ejecutar: 

     python tp_ping_srv.py port_number

> python tp_ping_serv.py 9000

El server levantará por default en el puerto *10000* si no se le especifica algún puerto.

### Cliente

Para ejecutar el comando ping directo contra el server (levantado en el puerto 9000):

    python tp_ping.py -c 5 -p -s 127.0.0.1:9000

Para ejecutar el comando ping reverso, 

	python tp_ping.py -c 5 -p -s 127.0.0.1:9000 -r

Para ejecutar el comando ping proxy, hay que levantar otra instancia del server (ej: 9001):

    python tp_ping.py -c 5 -p -s 127.0.0.1:9000 -x -d 127.0.0.1:9001