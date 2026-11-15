# Informe de validación — Tarea 5, Grupo 3

## Datos

- **Grupo:** 3
- **Componente:** Almacenamiento
- **Integrante:** Melvin Edgardo Peña Caballero
- **Número de cuenta:** 201230010100
- **Fecha de registro:** 14 de noviembre de 2026

> Este documento es el anexo de las pruebas recientes; no reemplaza la bitácora ni las capturas de la primera revisión. El [informe principal](./INFORME_TAREA5_G3.md) conserva esa documentación y agrega las pruebas nuevas en una sección de seguimiento.

## Alcance y criterio de lectura

Este informe coteja los diez requerimientos entregados por el estudiante con el código y con los resultados compartidos durante la sesión. Distingue entre implementación, pruebas realizadas por el estudiante, comprobaciones previas del asistente y acciones que se reservan para la exposición. Las pruebas de persistencia se hicieron en el proyecto aislado `g3-tarea5-validacion`, con el volumen `g3-tarea5-validacion-datos`; no se utilizó el volumen real `g3-inventario-datos`.

**Conclusión general:** los requisitos 1–5 están implementados y mayormente verificados; el requisito 7 se verificó también con `down -v` en el proyecto aislado. Los requisitos 6, 8, 9 y 10 quedan parciales por registros faltantes, evidencia del `docker build` no capturada o pasos reservados para la exposición.

## Matriz de los diez requerimientos

| N.º | Requerimiento | Comando o acción de validación | Resultado observado |
|---:|---|---|---|
| 1 | SQLite en `/datos/inventario.db`, `DB_PATH` y `POST /api/discos` | Revisar [sqlite_repository.py](./api/infrastructure/sqlite_repository.py) y [routes.py](./api/presentation/routes.py); registrar desde `http://localhost:8084/`; `curl -i http://localhost:8084/api/discos` | Implementado. Se registró un componente en la web aislada; después de `down`/`up`, el GET devolvió HTTP 200 y 6 registros (5 iniciales + 1 agregado). **Parcial:** la consigna pide registrar 3 componentes; se probó uno. |
| 2 | `Dockerfile.prod`: usuario `app`, `/datos` con permisos, `VOLUME /datos`, Gunicorn con 2 procesos y healthcheck cada 10 s sobre `/api/estado` | `docker exec g3-inventario-api-1 whoami`; `docker inspect --format 'estado={{.State.Health.Status}} healthcheck={{json .Config.Healthcheck.Test}}' g3-inventario-api-1` | Verificado: `whoami` devolvió `app`; estado `healthy`; el healthcheck consulta `/api/estado`. El Dockerfile declara dos workers y frecuencia de 10 s. |
| 3 | Web nginx, tabla, botón Actualizar y formulario POST; proxy `/api/` a `http://api:5000` | Revisar [web/app.js](./web/app.js) y [nginx.conf](./web/nginx.conf); `curl -i http://localhost:8083/`; registrar un componente desde el sitio aislado en `http://localhost:8084/` | Implementado. La página principal respondió HTTP 200; el proxy y el formulario se probaron en el stack aislado. |
| 4 | Compose con API/web, volumen `datos`, red `red-gN`, healthcheck, `depends_on: service_healthy`; solo web publica `808N:80` | `docker compose config --quiet`; `docker compose up -d api web`; `docker compose ps api web` | Compose válido. API `Up (healthy)` y web `Up`, puerto `8083:80`. Se añadió SQL Server como servicio extra. |
| 5 | API con `restart: unless-stopped`, CPU `0.50` y memoria `128M` | `docker inspect --format 'name={{.Name}} memory={{.HostConfig.Memory}} nano_cpus={{.HostConfig.NanoCpus}} pids={{.HostConfig.PidsLimit}}' g3-inventario-api-1 g3-inventario-web-1` | API: `134217728` bytes (128 MiB), `500000000` nano-CPU (0.50 CPU), 100 PIDs. Web: sin límites explícitos. |
| 6 | `docker compose up -d --build`; API healthy; registrar 3 componentes desde la página | `docker compose up -d api web`; stack aislado: `docker compose -p g3-tarea5-validacion -f - up -d` con API de Docker Hub y web local; formulario web | API healthy y web iniciada. Se guardó un componente en el volumen aislado y se verificó por API. **Parcial:** no se ejecutó el comando exacto `up -d --build` para todo el proyecto ni se registraron los 3 componentes requeridos. |
| 7 | `id`, `down`/`up` y persistencia; `down -v` y explicar pérdida | `docker exec ... whoami`; `docker compose -p g3-tarea5-validacion -f - down`; `docker compose ... down -v`; listar volúmenes; volver a levantar el Compose aislado; `curl -i http://localhost:8084/api/discos` | `whoami` devolvió `app`; con `down` sin `-v`, el registro persistió (6 registros). Con `down -v` se eliminó `g3-tarea5-validacion-datos`; `docker volume ls` confirmó su ausencia. Tras recrear el stack, GET respondió HTTP 200 con 5 registros semilla: el registro agregado se perdió. El volumen principal `g3-inventario-datos` permaneció. |
| 8 | Imagen `g3/estres:1.0` con `stress-ng`; ejecutar con 1.5 CPU, 512 MiB y 100 PIDs; registrar `docker stats` | `docker inspect ... g3-estres`; `docker update --cpus=1.5 g3-estres`; `docker start g3-estres`; `docker stats --no-stream g3-estres` | **Parcial:** la imagen existente `g3/estres:1.0` ejecutó la carga `stress-ng --cpu 2 --vm 1 --vm-bytes 128M --timeout 300s`. Límites confirmados: 1.5 CPU, 512 MiB, 100 PIDs. Stats: 147.61% CPU, 140.9 MiB / 512 MiB, 5 PIDs. No se conservó la salida del comando `docker build`. |
| 9 | Comparar `inspect` y cgroups; bajar CPU a 0.5; ejecutar `ls /proc/self/ns`, `hostname`, `ps -e` | `docker exec g3-estres sh -c '... cat /sys/fs/cgroup/cpu.max ... memory.max ... pids.max'`; `docker exec g3-estres sh -c 'ls /proc/self/ns && hostname && ps -e'`; `docker update --cpus=0.5 g3-estres` | Cgroups coinciden con `inspect`: `150000 100000`, `536870912`, `100`. Namespaces, hostname y procesos se listaron. **Parcial:** `docker update --cpus=0.5` se reserva para la exposición; el contenedor se mantiene en 1.5 CPU por ahora. |
| 10 | Etiquetar, subir, descargar y ejecutar `usuario/gN-recurso-api:1.0` en otro integrante | Docker Hub `penia93/g3-discos-api:1.0`; Docker Desktop Run, puerto `5050:5000`; `curl -i http://localhost:5050/api/estado`; `curl -i http://localhost:5050/api/discos` | Imagen pública y etiqueta `1.0` verificadas; se ejecutó en esta Mac. `/api/estado` respondió HTTP 200 y `/api/discos` devolvió 5 registros. **Parcial:** no se probó en el equipo de otro integrante. |

## Resultados y transcripciones importantes

### Compose principal

La primera ejecución de `docker compose config --quiet` desde `~` falló porque no encontró archivo de configuración. Desde la carpeta del proyecto terminó correctamente:

```text
compose valido
```

`docker compose ps api web` mostró:

```text
g3-inventario-api-1   Up (healthy)   5000/tcp
g3-inventario-web-1   Up             0.0.0.0:8083->80/tcp
```

Las consultas al sitio y a la API respondieron:

```text
GET http://localhost:8083/api/estado  -> HTTP 200, estado "ok"
GET http://localhost:8083/api/discos  -> HTTP 200, total 5
GET http://localhost:8083/            -> HTTP 200, Content-Type text/html
```

### Persistencia en el proyecto de prueba

El proyecto `g3-tarea5-validacion` se levantó usando una configuración Compose enviada por heredoc (`-f -`), sin modificar el `compose.yaml` principal. Usó la imagen pública de API, la imagen local de web, puerto `8084`, red `g3-tarea5-validacion-red` y volumen `g3-tarea5-validacion-datos`.

Después de agregar un componente desde la página, `docker compose down` quitó los contenedores y la red, pero conservó el volumen. Tras levantar el mismo stack, la consulta devolvió:

```text
HTTP/1.1 200 OK
...
"id":6,"marca":"SAMSUNG_2","modelo":"990 PRO_2","tipo":"SSD"
...
"total":6
```

Esto confirmó que el componente de prueba persistió junto con los cinco registros iniciales.

Luego se ejecutó `docker compose -p g3-tarea5-validacion -f - down -v` usando una configuración que declara explícitamente el volumen aislado `g3-tarea5-validacion-datos`. Docker reportó la eliminación de los contenedores API/web y de ese volumen. `docker volume ls` mostró que el volumen de prueba ya no existía y que `g3-inventario-datos` seguía presente.

Se levantó nuevamente el stack aislado, lo que creó un volumen vacío. El contenedor web terminó inicialmente porque nginx no resolvió el upstream `api` al arrancar. La API estaba healthy; al iniciar de nuevo el contenedor web, la consulta funcionó:

```text
curl -i http://localhost:8084/api/discos
HTTP/1.1 200 OK
"total":5
```

La respuesta incluyó los cinco registros semilla y no el componente de prueba `SAMSUNG_2`. Esto demuestra que `down -v` elimina el volumen y los datos persistidos en él. El error tipográfico `docker volumne ls` no afectó el entorno; el comando correcto `docker volume ls` se ejecutó después.

### Prueba de carga

El contenedor `g3-estres` ya existía. Su configuración inicial era `0.5 CPU`, `512 MiB` y `100 PIDs`, y estaba detenido. Se actualizó a 1.5 CPU, se inició y se observó la carga:

```text
docker stats --no-stream g3-estres
CPU: 147.61%
Memoria: 140.9MiB / 512MiB
PIDs: 5
```

La lectura de cgroups dentro del contenedor fue:

```text
cpu.max=150000 100000
memory.max=536870912
pids.max=100
```

También se ejecutó `ls /proc/self/ns`, `hostname` y `ps -e`. El hostname observado fue `eef4578461b7`; la lista mostró `stress-ng` y sus procesos de CPU y memoria. La carga tiene `--timeout 300s` y se detiene sola después de cinco minutos.

### Imagen publicada

Docker Hub muestra el repositorio público [penia93/g3-discos-api](https://hub.docker.com/r/penia93/g3-discos-api) con tag `1.0`. El contenedor local de prueba respondió en el puerto `5050`; el endpoint de salud devolvió HTTP 200 y el inventario devolvió cinco discos. Esto verifica publicación y ejecución local, no la prueba en el equipo de otro integrante.

## Acciones reservadas para la exposición en vivo

1. **Requerimiento 6:** si se quiere completar literalmente, registrar dos componentes adicionales en la base aislada; hasta ahora se confirmó uno.
2. **Requerimiento 9:** ejecutar `docker update --cpus=0.5 g3-estres` y volver a inspeccionar/leer cgroups. El contenedor se mantiene en 1.5 CPU hasta esa demostración.
3. **Requerimiento 10:** descargar y correr `penia93/g3-discos-api:1.0` en el equipo de otro integrante. La ejecución hecha en esta Mac no sustituye esa comprobación.

## Validación previa aislada realizada por el asistente

Antes de acordar que el usuario ejecutaría los comandos paso a paso, se creó un contenedor/volumen temporal independiente. Se probó un POST y persistencia tras recrear el contenedor, y se ejecutó `docker update` en ese recurso. El usuario indicó que limpió esos recursos. Esa prueba no modificó la base real ni cuenta como evidencia ejecutada por el estudiante.

## Capturas disponibles para comparación

Se incluyen las capturas disponibles en el proyecto y la captura adjunta durante la sesión. Se agregan al PDF como anexo visual y se dejan aquí referenciadas para cotejo:

- **Interfaz inventario (captura recortada):** [evidencia_inventario_web.png](./evidencia_inventario_web.png). Muestra el panel y los cinco registros; no se ve la fecha/hora del equipo.
- **Estado de API (captura gráfica):** [evidencia_api_estado.png](./evidencia_api_estado.png). Muestra el estado `ok` y una fecha UTC renderizada por la aplicación; no es una captura completa de navegador/terminal.
- **Navegador completo, localhost:8084:** [evidencia_web_completa.png](./evidencia_web_completa.png). Muestra el navegador, el panel con cinco dispositivos y la fecha/hora de macOS. Se incluye para comparar la interfaz tras recrear el volumen.

Estas capturas son las imágenes disponibles para comparación; las salidas de comandos y las respuestas HTTP se documentan como texto en las secciones anteriores. Para entregar como evidencia formal, deben tomarse capturas completas de cada prueba con la fecha y hora del equipo visibles.

![Interfaz inventario](./evidencia_inventario_web.png)

![Estado API](./evidencia_api_estado.png)

![Navegador completo localhost:8084](./evidencia_web_completa.png)

### Capturas compartidas anteriormente (anexadas completas)

Se agregan las 14 capturas proporcionadas en las sesiones, en orden cronológico. Las dos capturas suplementarias generadas para la interfaz y el estado de API también permanecen en este anexo.

![01 — Docker Hub, etiqueta 1.0 de la API](./evidencia_compartida_01_revision_previa.png)

![02 — Docker Desktop, contenedores y consumo](./evidencia_compartida_02_revision_previa.png)

![03 — Estado de la API en el navegador](./evidencia_compartida_03_estado_api.png)

![04 — Búsqueda del repositorio de Docker Hub](./evidencia_compartida_04_busqueda_dockerhub.png)

![05 — Diálogo de ejecución de la imagen pública](./evidencia_compartida_05_run_imagen.png)

![06 — Rechazo del nombre de contenedor ingresado](./evidencia_compartida_06_error_nombre.png)

![07 — Vista de contenedores en Docker Desktop](./evidencia_compartida_07_contenedores.png)

![08 — Logs de Gunicorn en el contenedor de API pública](./evidencia_compartida_08_logs_api_publica.png)

![09 — Vista de contenedores y API local](./evidencia_compartida_09_contenedores.png)

![10 — Vista de Docker Desktop durante la prueba del stack aislado](./evidencia_compartida_10_docker_prueba.png)

![11 — Interfaz mostrando el registro agregado de prueba](./evidencia_compartida_11_registro_prueba.png)

![12 — Vista de contenedores durante las comprobaciones](./evidencia_compartida_12_contenedores.png)

![13 — Docker Desktop durante la prueba de estrés](./evidencia_compartida_13_stress_ng.png)
