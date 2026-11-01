# Guía Funcional de EchoNotes

## Objetivo del documento

Esta guía describe cómo operar EchoNotes desde el punto de vista funcional. Su objetivo es que músicos, estudiantes, docentes y personal de soporte sepan cómo trabajar con cada sección disponible en la interfaz web y en la línea de comandos, y entiendan el alcance real de los módulos implementados en el backend y el frontend.

La guía está basada en las pantallas, rutas y módulos actualmente desarrollados en el proyecto.

## Alcance funcional actual

El sistema permite trabajar con estas áreas:

- Carga de un archivo de audio (selección o arrastrar y soltar) o uso de una pista de ejemplo.
- Selección opcional de los instrumentos esperados en la pista.
- Transcripción con visualización en tiempo real en un piano roll.
- Reproducción del resultado, mezclando o separando el audio original y la síntesis MIDI.
- Silenciar o aislar (solo) instrumentos y resaltar sus notas.
- Descarga del resultado como archivo MIDI.
- Descarga de audio WAV sintetizado (solo transcripción o estéreo con el original).
- Generación y descarga de partituras en PDF, MusicXML y tablaturas.
- Consulta de preguntas frecuentes.
- Uso equivalente desde la línea de comandos (CLI) y desde la API HTTP.

## Consideraciones importantes antes de operar

Antes de usar el sistema conviene tener claras estas reglas:

1. EchoNotes no requiere usuarios ni contraseñas: cualquier persona con acceso a la URL del servidor puede usarlo.
2. El servidor necesita haber descargado los pesos del modelo desde HuggingFace, lo que exige aceptar la licencia del modelo e iniciar sesión una vez (ver README).
3. Los pesos del modelo están bajo licencia CC BY-NC 4.0: el sistema solo puede usarse con fines no comerciales.
4. El servidor procesa **una transcripción a la vez**. Si otra persona está transcribiendo, la interfaz espera y reintenta automáticamente.
5. Las partituras en PDF requieren que el servidor tenga instalado MuseScore 4 o superior. Sin él, todo lo demás funciona.
6. La exportación a WAV requiere FluidSynth en el servidor.
7. Si se indican instrumentos antes de transcribir, **ningún otro instrumento podrá aparecer** en el resultado.
8. El audio subido se procesa en el servidor y no se guarda después de la transcripción.

## Flujo recomendado de configuración inicial

Para poner a funcionar EchoNotes desde cero, el orden recomendado es este:

1. Instalar Python, uv, Node.js y pnpm (ver README).
2. Instalar las dependencias del backend (`uv sync`) y del frontend (`pnpm install`).
3. Aceptar la licencia del modelo en HuggingFace e iniciar sesión (`uvx hf auth login`).
4. Opcional: instalar MuseScore 4 para partituras y FluidSynth para audio WAV.
5. Compilar el frontend (`pnpm run build` dentro de `web/`).
6. Iniciar el servidor con `uv run echonotes serve` (agregar `--model small` si el equipo no tiene GPU).
7. Abrir `http://127.0.0.1:8222` en el navegador.
8. Probar con la pista de ejemplo antes de usar audio propio.

## Acceso a la aplicación

### Qué hace esta sección

Al abrir la aplicación, el navegador consulta `GET /health` para comprobar que el servidor está disponible y `GET /instruments` para cargar la lista de instrumentos.

### Cómo usarla

1. Abrir la URL del servidor en el navegador.
2. Esperar a que aparezca el recuadro para cargar audio.

### Resultado esperado

- Si el servidor responde, se muestra la pantalla de bienvenida con el botón `Seleccionar archivo de audio`.
- Si el servidor no responde, el recuadro muestra `no disponible` con el mensaje "El servidor de EchoNotes no está disponible en este momento". Al recargar la página cuando el servidor vuelva, la pantalla se restablece.

## Tipos de usuario y responsabilidades funcionales

### Usuario de la interfaz web

Músico, estudiante o docente que quiere obtener la transcripción de una canción.

Puede:

- Cargar un archivo de audio o usar la pista de ejemplo.
- Indicar los instrumentos esperados.
- Ver la transcripción en tiempo real.
- Reproducir, comparar y explorar el resultado.
- Descargar MIDI, WAV, partituras y tablaturas.

### Usuario de línea de comandos

Persona técnica que necesita transcribir varios archivos o integrar EchoNotes en un flujo automatizado.

Puede:

- Transcribir un archivo a MIDI, JSON, JSONL o partituras.
- Elegir el tamaño del modelo y el dispositivo (CPU, GPU, MPS).
- Restringir los instrumentos.
- Generar una auralización estéreo (original + síntesis).
- Listar los instrumentos disponibles.

### Administrador del servidor

Responsable de instalar y mantener el servicio.

Puede:

- Instalar dependencias, MuseScore y FluidSynth.
- Configurar el acceso a HuggingFace (`HF_TOKEN`).
- Iniciar el servidor (`echonotes serve`) o desplegarlo con Docker.
- Elegir el modelo según el hardware disponible.

## Configuración según tipo de equipo

EchoNotes funciona en distintos equipos; el tamaño del modelo debe elegirse según el hardware disponible usando la opción `--model`.

### 1. Equipo con GPU NVIDIA

Uso recomendado:

- Usar el modelo `medium` (por defecto) o `large` para máxima precisión.
- En Windows, PyTorch se instala por defecto solo para CPU; para usar la GPU hay que instalarlo con soporte CUDA (por ejemplo con la opción `--torch-backend=cu128` de uv).

Ejemplo operativo:

1. `uv run echonotes serve --model large`

### 2. Mac con Apple Silicon (M1, M2, M3, …)

Uso recomendado:

- El modelo se ejecuta automáticamente en la GPU del Mac (Metal/MPS).
- El modelo `medium` ofrece un buen equilibrio.

Ejemplo operativo:

1. `uv run echonotes serve`

### 3. Equipo solo con CPU o Mac con procesador Intel

Uso recomendado:

- Usar el modelo `small`; los modelos más grandes funcionan pero son mucho más lentos.
- En Mac Intel crear el entorno con Python 3.12 (ver README, paso 1).

Ejemplo operativo:

1. `uv run echonotes serve --model small`

### Regla general de configuración

Si la transcripción tarda demasiado, bajar el tamaño del modelo; si la precisión es insuficiente y hay GPU disponible, subirlo.

## Guía funcional por secciones del frontend

## Pantalla de bienvenida

### Cargar audio

#### Objetivo

Seleccionar el archivo de audio que se va a transcribir.

#### Qué puede hacer el usuario

- Seleccionar un archivo con el botón `Seleccionar archivo de audio`.
- Arrastrar un archivo y soltarlo en cualquier parte de la página.
- Cargar la pista de ejemplo con `o prueba con una pista de ejemplo`.
- Cambiar el archivo elegido con `Elegir otro archivo`.

#### Formatos soportados

- MP3, WAV, FLAC, OGG, M4A, AAC, AIFF y Opus.

#### Cómo usarla

1. Presionar `Seleccionar archivo de audio` o arrastrar el archivo a la página.
2. Verificar que el nombre del archivo aparece en el recuadro.
3. Continuar con la selección de instrumentos (opcional).

#### Resultado funcional

El archivo queda seleccionado, pero la transcripción **no comienza** hasta presionar `Transcribir`.

### Selección de instrumentos

#### Objetivo

Indicar al modelo qué instrumentos hay en la pista para mejorar la precisión.

#### Datos que maneja

- Lista de instrumentos seleccionados (etiquetas).
- Catálogo de 35 grupos de instrumentos del modelo: pianos, guitarras, bajos, cuerdas, metales, maderas, saxofones, sintetizadores, voz, batería, etc.

#### Cómo usarla

1. Escribir en el campo `Agregar un instrumento…` (por ejemplo `guitarra`, `violin`, `metales` o `bateria`; la búsqueda acepta español o inglés, con o sin tildes, y tolera errores de escritura).
2. Elegir la sugerencia con el ratón o con las flechas y `Enter`.
3. Para quitar un instrumento, presionar la `×` de su etiqueta o `Retroceso` con el campo vacío.
4. Para vaciar la lista, presionar `Limpiar`.

#### Reglas funcionales

- La selección es **opcional**. Si se deja vacía, el modelo detecta los instrumentos automáticamente.
- Si se seleccionan instrumentos, el modelo **no podrá** generar notas de ningún otro.
- Al usar la pista de ejemplo, la lista se completa con una sugerencia (batería, bajo eléctrico, guitarras y voz).

### Iniciar la transcripción

#### Objetivo

Enviar el audio al servidor para comenzar la transcripción.

#### Cómo usarla

1. Presionar `Transcribir`.
2. Si el servidor está ocupado, el botón muestra `Servidor ocupado, reintentando en N s` y reintenta solo.
3. Para desistir mientras espera, presionar `Cancelar`.

#### Resultado funcional

Cuando el servidor acepta el audio, la aplicación pasa a la vista de transcripción. Si el archivo no se puede leer, se vuelve a la pantalla de bienvenida con un mensaje en rojo (por ejemplo, "no se pudo decodificar el archivo de audio").

## Vista de transcripción

### Barra de reproducción

#### Objetivo

Escuchar y explorar el resultado.

#### Qué muestra

- Botón `Reproducir` / `Pausa` (también con la barra espaciadora).
- Botón `Seguir cursor`: la vista se desplaza junto con la reproducción.
- Reloj con el segundo actual.
- Control deslizante `Original` ↔ `MIDI` para mezclar el audio original con la síntesis de las notas transcritas.
- Casilla `Estéreo`: el original suena por el canal izquierdo y la síntesis por el derecho (desactiva el control de mezcla).

#### Uso operativo

Comparar el original con la síntesis permite detectar notas faltantes o sobrantes de forma auditiva.

### Piano roll

#### Objetivo

Visualizar las notas transcritas en el tiempo, con un color por instrumento.

#### Qué muestra

- Teclado vertical a la izquierda (altura de cada nota).
- Notas como barras de color que aparecen a medida que avanza la transcripción.
- Cuadrícula de compases y pulsos cuando se detecta el tempo.
- Línea azul de reproducción (cursor).

#### Cómo usarla

- Clic o arrastrar sobre las notas: mover el cursor de reproducción.
- `Ctrl`/`Cmd` + rueda (o pellizcar en el trackpad): zoom en el tiempo.
- `Alt`/`Option` + rueda o arrastrar sobre el teclado: zoom en la altura.
- `Shift` + rueda: desplazarse en el tiempo; rueda sola: desplazarse en la altura.
- En pantallas táctiles: un dedo desplaza, dos dedos hacen zoom.

### Lista de instrumentos

#### Objetivo

Ver qué instrumentos se detectaron y controlar su sonido y visibilidad.

#### Qué muestra

- Un color por instrumento (el mismo del piano roll).
- Botón `S` (solo): escuchar únicamente ese instrumento.
- Botón de altavoz: silenciar el instrumento en la pista MIDI.
- Instrumentos indicados que no se detectaron, tachados y marcados `no detectado`.

#### Uso operativo

Pasar el ratón sobre un instrumento resalta sus notas en el piano roll y atenúa las demás.

### Barra de salida y descargas

#### Objetivo

Seguir el progreso y exportar el resultado.

#### Qué muestra

- Barra de progreso con el tiempo transcrito y el tiempo estimado restante (`termina en …`).
- Botón `Descargar` (se habilita al terminar) con estas opciones:
  - `Archivo MIDI`.
  - `WAV - solo transcripción`: las notas tocadas con un SoundFont (mono).
  - `WAV - estéreo con el original`: original a la izquierda y síntesis a la derecha.
  - `Partituras`: abre el diálogo de partituras.
- Botón `Transcribir otro archivo` (pide confirmación porque descarta el resultado actual).

#### Resultado funcional

Los archivos se descargan con el nombre del audio original (por ejemplo `cancion_mezcla.wav`, `cancion_partituras.zip`).

### Diálogo de partituras

#### Objetivo

Descargar la partitura generada con MuseScore.

#### Qué muestra

- `Archivo MIDI` cuantizado (`score.mid`).
- `Partitura MusicXML` (`score.musicxml`), editable en MuseScore, Sibelius o Guitar Pro.
- `Partitura completa – todos los instrumentos` (`full_score.pdf`).
- Un PDF por instrumento y una tablatura por cada instrumento de trastes (guitarra, bajo).
- Tamaño de cada archivo.

#### Cómo usarla

1. En `Descargar`, elegir `Partituras` y esperar a que se generen (`Generando…`).
2. Hacer clic en cada archivo para descargarlo, o en `Descargar todo` para obtener el ZIP.
3. Cerrar con `Cerrar` o `Esc`.

#### Consideración importante

Si no se encontró un pulso estable, el diálogo avisa que las barras de compás son aproximadas y la partitura puede ser difícil de leer.

## Preguntas frecuentes

Debajo de la pantalla de bienvenida hay una sección de preguntas frecuentes con información sobre formatos, instrumentos, precisión, privacidad, licencias y funcionamiento técnico. Se abren y cierran con un clic.

## Uso desde la línea de comandos

### Transcribir un archivo

```bash
uv run echonotes transcribe cancion.mp3
```

Genera `cancion.mid` junto al audio.

| Opción | Descripción |
|---|---|
| `-o, --output` | Ruta de salida (`-` para stdout) |
| `-f, --format` | `midi` (por defecto), `json`, `jsonl` o `sheets` |
| `-m, --model` | `small`, `medium` (por defecto), `large` o ruta a pesos |
| `-d, --device` | `auto`, `cpu`, `cuda`, `mps` |
| `--instruments` | Lista separada por comas (por ejemplo `piano,voice`) |
| `--detect-tempo` | `true`, `false` o `best-effort` (por defecto) |
| `--auralize` | Escribe un WAV/MP3 estéreo original + síntesis |

### Generar partituras

```bash
uv run echonotes transcribe cancion.mp3 --format sheets --output partitura/
```

### Listar instrumentos

```bash
uv run echonotes list-instruments
```

### Iniciar el servidor

```bash
uv run echonotes serve --model small --port 8222
```

## Relación funcional entre frontend y backend

Cada área del frontend consume rutas específicas del backend:

- Acceso a la aplicación usa `GET /health`.
- Selección de instrumentos usa `GET /instruments`.
- Transcripción y piano roll usan `POST /transcribe` (flujo SSE).
- Descarga WAV usa `POST /auralize`.
- Diálogo de partituras usa `POST /sheets`.
- Reproducción MIDI en el navegador usa `GET /soundfonts/MuseScore_General.sf3`.
- La descarga MIDI no consulta al servidor: el archivo llega al final del flujo de `/transcribe`.

Esto significa que la operación visible en el frontend depende directamente de esas capacidades expuestas en el backend.

## Orden de uso recomendado para una transcripción

Un ciclo típico de uso del sistema debería seguir esta secuencia:

1. Preparar un audio de buena calidad, idealmente con tempo estable.
2. Cargarlo en la pantalla de bienvenida.
3. Indicar los instrumentos si se conocen.
4. Presionar `Transcribir` y seguir el progreso en el piano roll.
5. Revisar el resultado escuchando la mezcla original/MIDI y aislando instrumentos.
6. Descargar el MIDI para editarlo en un DAW, o las partituras y tablaturas para leerlas.
7. Presionar `Transcribir otro archivo` para continuar con la siguiente pista.

## Limitaciones funcionales actuales

Para operar correctamente el sistema, es importante considerar estas limitaciones de la versión actual:

1. Solo se procesa una transcripción a la vez por servidor.
2. Sin MuseScore 4 no se pueden generar partituras en PDF.
3. Las partituras pierden legibilidad con grabaciones sin tempo estable (rubato).
4. No genera cifrado de acordes, solo las notas que se tocan.
5. Funciona mejor con música acústica y de guitarra que con música electrónica.
6. El endpoint bloqueante `/transcribe/midi` rechaza audios de más de 15 minutos.
7. No hay cuentas de usuario ni historial: los resultados deben descargarse antes de cerrar la página.
8. Los pesos del modelo solo pueden usarse con fines no comerciales (CC BY-NC 4.0).

## Recomendaciones de operación

1. Probar primero con la pista de ejemplo para validar la instalación.
2. Indicar los instrumentos cuando se conozcan; mejora la precisión y evita instrumentos fantasma.
3. Usar el modelo `small` en equipos sin GPU.
4. Preferir grabaciones con metrónomo o tempo estable si el objetivo es la partitura.
5. Revisar y corregir el MIDI en un editor (MuseScore, DAW) antes de usarlo como partitura definitiva.

## Resumen ejecutivo de uso

En la práctica, el sistema se usa así:

1. El administrador instala EchoNotes, inicia sesión en HuggingFace e inicia el servidor.
2. El usuario abre la web, carga un audio e indica (opcionalmente) los instrumentos.
3. EchoNotes transcribe la pista y muestra las notas en tiempo real.
4. El usuario explora el resultado y descarga MIDI, audio, partituras o tablaturas.

Con esa secuencia, EchoNotes cubre la transcripción musical de audio a notación dentro del alcance actualmente implementado.
