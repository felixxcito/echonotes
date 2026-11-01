<p align="center">
  <img src="web/public/echonotes-logo-full.svg" alt="Logo de EchoNotes" width="340">
</p>

# EchoNotes

Aplicación web y de línea de comandos para la **transcripción musical automática**: recibe una grabación de audio (mp3, wav, flac, …) y obtiene las notas que toca cada instrumento en formato **MIDI**, **partituras en PDF**, **MusicXML** y **tablaturas** de guitarra y bajo. El proyecto está dividido en dos partes dentro del mismo repositorio: un backend en Python (modelo de IA + API REST con FastAPI + CLI) y un frontend web desarrollado con React + Vite.

EchoNotes es una copia modificada de [MuScriptor](https://github.com/muscriptor/muscriptor), el modelo abierto de transcripción multiinstrumento de Kyutai y Mirelo (código bajo licencia MIT). Para este proyecto se cambió el nombre, la estética (tema claro), el idioma de la interfaz y del CLI (español) y se agregó la documentación del sistema.

El sistema está orientado a estos tipos de usuario:

- Usuario de la interfaz web (músico, estudiante o docente de música)
- Usuario de línea de comandos (transcripciones por lotes o automatizadas)
- Desarrollador o integrador (uso de la API HTTP o de la librería de Python)

Entre las funciones principales se incluyen la carga de audio, la selección opcional de instrumentos esperados, la transcripción en tiempo real con un piano roll interactivo, la reproducción comparando el audio original con la síntesis MIDI, la descarga de MIDI y audio WAV, y la generación de partituras y tablaturas.

## Estructura del proyecto

```text
echonotes/
├── echonotes/          # Paquete de Python: modelo, API (FastAPI) y CLI (Typer)
│   ├── models/         # Modelo de lenguaje (transformer decoder-only)
│   ├── modules/        # Transformer en streaming, condicionadores, espectrograma mel
│   ├── tokenizer/      # Tokenizador MT3 y estructuras de notas
│   ├── utils/          # Audio, tempo, MIDI, partituras, auralización, descargas
│   ├── server.py       # API HTTP (FastAPI)
│   ├── main.py         # Interfaz de línea de comandos (CLI)
│   └── web_dist/       # Frontend compilado (se genera con `pnpm run build`)
├── web/                # Aplicación web con React, Vite y Tailwind CSS
├── tests/              # Pruebas automatizadas con pytest
├── Dockerfile          # Imagen con backend + frontend + MuseScore
├── pyproject.toml      # Dependencias y metadatos del paquete de Python
├── README.md
└── GUIA_FUNCIONAL.md   # Guía de uso funcional del sistema
```

## Requisitos

- Python 3.10, 3.11 o 3.12 (3.13 también funciona salvo en Mac con procesador Intel)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (gestor de entornos y paquetes de Python)
- Node.js 20.19 o superior (recomendado 22) y [pnpm](https://pnpm.io/installation) (también funciona con npm)
- Una cuenta gratuita de [HuggingFace](https://huggingface.co) con la licencia del modelo aceptada
- Opcional: **MuseScore 4** o superior, para generar partituras y tablaturas en PDF ([descarga](https://musescore.org/es/download))
- Opcional: **FluidSynth**, para exportar la transcripción como audio WAV

## Puesta en marcha

### 1. Instalar dependencias

Backend (desde la carpeta raíz del proyecto):

```bash
uv sync
```

En Mac con procesador **Intel** el archivo `uv.lock` no trae ruedas de `torchaudio` para esa plataforma, así que hay que crear el entorno con Python 3.12 e instalar sin el lock:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -e . pytest
```

Frontend:

```bash
cd web
pnpm install
```

### 2. Configurar HuggingFace y variables de entorno

Los pesos del modelo se publican en HuggingFace bajo la licencia **CC BY-NC 4.0** (uso no comercial) y requieren aceptar la licencia una sola vez:

1. Entrar a la página del modelo [small](https://huggingface.co/MuScriptor/muscriptor-small), [medium](https://huggingface.co/MuScriptor/muscriptor-medium) o [large](https://huggingface.co/MuScriptor/muscriptor-large) y aceptar la licencia (el acceso se concede automáticamente).
2. Iniciar sesión en el equipo:

```bash
uvx hf auth login
```

o bien definir un token de lectura creado en [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens):

```bash
export HF_TOKEN=hf_...
```

Los pesos se descargan automáticamente en el primer uso y quedan en caché.

Variables de entorno reconocidas:

| Variable | Uso |
|---|---|
| `HF_TOKEN` | Token de HuggingFace para descargar los pesos del modelo |
| `ECHONOTES_MUSESCORE` | Ruta al ejecutable de MuseScore si no está en una ubicación estándar |
| `BACKEND_URL` | (Solo frontend en desarrollo) servidor al que Vite reenvía la API; por defecto `http://127.0.0.1:8222` |
| `VITE_GA_MEASUREMENT_ID` | (Opcional, al compilar el frontend) activa Google Analytics con banner de consentimiento; vacío = sin analítica |

### 3. Compilar el frontend y ejecutar el backend

```bash
cd web
pnpm run build
cd ..
uv run echonotes serve
```

`pnpm run build` deja la web compilada en `echonotes/web_dist/`, y `echonotes serve` sirve la interfaz y la API en el mismo puerto.

Aplicación disponible en `http://127.0.0.1:8222`

Opciones útiles: `--model small` (recomendado si solo hay CPU), `--port 8222`, `--host 0.0.0.0`.

### 4. Ejecutar el frontend en modo desarrollo

Con el backend corriendo en el puerto 8222:

```bash
cd web
pnpm dev
```

Aplicación disponible en `http://localhost:5173` (con recarga automática al editar).

Para probar solo la interfaz sin descargar el modelo, `pnpm run dev:proxy` reenvía la API al servidor público de demostración del proyecto original (`muscriptor.kyutai.org`). Úsalo solo para pruebas: el audio que subas se procesa en ese servidor externo.

## Backend

El paquete `echonotes/` contiene el modelo de transcripción, una API REST construida con FastAPI y una interfaz de línea de comandos construida con Typer. Su responsabilidad es cargar el modelo, procesar el audio, generar los eventos de notas y exportar los resultados.

### Stack principal

- Python
- PyTorch (CUDA, Apple Metal/MPS o CPU)
- FastAPI + Uvicorn
- Typer (CLI)
- huggingface_hub + safetensors (descarga y carga de pesos)
- mido (MIDI) y soundfile (lectura de audio)
- beat-this (detección de tempo y compases)
- MuseScore 4 (grabado de partituras, vía su CLI)
- FluidSynth (síntesis de audio a partir del MIDI)

### Organización principal

- `transcription_model.py`: clase `TranscriptionModel`, punto de entrada del dominio. Carga los pesos, divide el audio en fragmentos de 5 segundos, genera tokens y los convierte en eventos de notas y en MIDI.
- `models/lm.py`: `LMModel`, el transformer decoder-only que genera los tokens.
- `modules/`: transformer en streaming con caché de atención (`StreamingTransformer`), condicionadores de audio (espectrograma mel) y de instrumentos.
- `tokenizer/`: tokenizador MT3 (vocabulario de eventos de nota, tiempo e instrumento) y estructuras `Note` / `NoteEvent`.
- `events.py`: eventos que emite la transcripción (`NoteStartEvent`, `NoteEndEvent`, `ProgressEvent`).
- `utils/beats.py`: detección de tempo, compás y cuadrícula de pulsos (`BeatGrid`).
- `utils/midi.py`: exportación y cuantización del MIDI.
- `utils/sheets.py`: generación de partituras, partes por instrumento y tablaturas con MuseScore.
- `utils/auralization.py`: síntesis del MIDI con un SoundFont y mezcla con el audio original.
- `utils/download.py`: descarga y caché de pesos y SoundFonts.
- `server.py`: API HTTP.
- `main.py`: CLI (`transcribe`, `serve`, `list-instruments`).

### Endpoints de la API

| Método y ruta | Descripción |
|---|---|
| `GET /health` | Verifica que el servidor esté activo |
| `GET /instruments` | Lista los 35 grupos de instrumentos que reconoce el modelo |
| `POST /transcribe` | Recibe un audio (`file`) y, opcionalmente, instrumentos; responde un flujo SSE con las notas en tiempo real y, al final, el MIDI en base64 y la cuadrícula de tempo |
| `POST /transcribe/midi` | Igual que el anterior pero bloqueante: devuelve directamente el archivo `.mid` (máximo 15 minutos de audio) |
| `POST /auralize` | Recibe un MIDI (y el audio original en modo `mix`) y devuelve un WAV sintetizado |
| `POST /sheets` | Recibe un MIDI y devuelve un ZIP con MusicXML, partitura completa, PDF por instrumento y tablaturas |
| `GET /soundfonts/MuseScore_General.sf3` | SoundFont que usa el navegador para reproducir el MIDI |

La documentación interactiva de FastAPI queda disponible en `http://127.0.0.1:8222/docs`.

### Modelos disponibles

| Variante | Parámetros | Capas | Dimensión | Uso recomendado |
|---|---|---|---|---|
| `small` | 103M | 14 | 768 | Equipos solo con CPU |
| `medium` (por defecto) | 307M | 24 | 1024 | Equilibrio velocidad / precisión |
| `large` | 1.4B | 48 | 1536 | Máxima precisión, requiere GPU |

### Concurrencia

El servidor procesa una transcripción a la vez. Si llega otra mientras hay una en curso responde `503` (servidor ocupado) y la interfaz web reintenta automáticamente. Una nueva solicitud del mismo navegador (identificado por la cabecera `X-Client-Id`) cancela la anterior.

### Comandos disponibles

```bash
uv run echonotes serve                                   # Interfaz web + API
uv run echonotes transcribe cancion.mp3                  # Audio → MIDI
uv run echonotes transcribe cancion.mp3 -f sheets -o partitura/   # Partituras PDF + MusicXML
uv run echonotes transcribe cancion.mp3 --instruments piano,voice # Restringir instrumentos
uv run echonotes list-instruments                        # Nombres de instrumentos válidos
uv run echonotes --help                                  # Ayuda completa
```

## Frontend

La carpeta `web/` contiene la interfaz web del sistema. Es una SPA (aplicación de una sola página) construida con React con un flujo de dos pantallas: bienvenida/carga de audio y vista de transcripción.

### Stack principal

- React 19
- TypeScript
- Vite 8
- Tailwind CSS 4
- Tone.js (reproducción y transporte de audio)
- spessasynth_lib (síntesis del MIDI en el navegador con SoundFont)
- fflate (descompresión del ZIP de partituras)

### Organización principal

- `src/App.tsx`: componente raíz; controla la pantalla actual y el estado de la transcripción.
- `src/components/`: componentes visuales (`WelcomeScreen`, `ConditioningPanel`, `Controls`, `PianoRollCanvas`, `InstrumentList`, `OutputBar`, `SheetsDialog`, `Faq`, `Footer`, …).
- `src/hooks/`: `useTranscription` (envía el audio y procesa el flujo SSE) y `useAudioEngine`.
- `src/audio.ts`: motor de audio (`AudioEngine`) que reproduce el original y las notas transcritas.
- `src/pianoroll.ts`: dibujo del piano roll en un `<canvas>` (`PianoRoll`).
- `src/sse.ts`: cliente del flujo SSE con reintentos.
- `src/instruments.ts`: nombres en español de los instrumentos y búsqueda tolerante a tildes y errores.
- `src/project.ts`: datos del proyecto (contacto, repositorio, créditos).
- `src/style.css`: tokens de diseño del tema claro de EchoNotes (colores, tipografías, sombras).

### Tema visual

Toda la paleta está centralizada en `web/src/style.css` (bloque `@theme` y variables `--roll-*` del piano roll): fondo `#f7f8fb`, tarjetas blancas, acento azul `#2563eb`, tipografías Inter y Playfair Display. Los logos están en `web/public/` (`echonotes-logo.svg`, `echonotes-mark.svg`, `echonotes-wave.svg`, `echonotes-logo-full.svg`).

### Comunicación con el backend

Vite está configurado para trabajar en desarrollo con un proxy hacia el backend:

- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8222`
- Rutas reenviadas: `/transcribe`, `/instruments`, `/auralize`, `/sheets`, `/health`, `/soundfonts`

En producción el backend sirve directamente los archivos compilados de `echonotes/web_dist/`.

### Scripts disponibles

```bash
pnpm dev          # Servidor de desarrollo con recarga automática
pnpm dev:proxy    # Desarrollo usando el servidor público de demostración como backend
pnpm run build    # Verificación de tipos + compilación a echonotes/web_dist
pnpm preview      # Sirve la versión compilada
```

## Flujo general del sistema

1. El usuario abre la aplicación web y selecciona o arrastra un archivo de audio.
2. Opcionalmente indica qué instrumentos hay en la pista.
3. El frontend envía el audio a `POST /transcribe`.
4. El backend divide el audio en fragmentos de 5 segundos y el modelo genera, para cada uno, tokens de notas e instrumentos.
5. Cada nota decodificada se envía al navegador como evento SSE y aparece en el piano roll en tiempo real.
6. Al terminar, el backend detecta el tempo, arma el MIDI final y lo envía junto con la cuadrícula de compases.
7. El usuario reproduce, compara con el original, silencia o aísla instrumentos y descarga MIDI, WAV o partituras (que el backend genera con MuseScore).

## Pruebas

```bash
uv run pytest -q
```

Las pruebas de `tests/test_integration.py` necesitan los pesos reales del modelo (requieren el login de HuggingFace). El resto de la suite (221 pruebas) corre sin descargar el modelo:

```bash
uv run pytest -q --deselect tests/test_integration.py
```

## Docker

```bash
docker build -t echonotes .
docker run -p 8000:8000 -e HF_TOKEN=hf_... echonotes
```

La imagen incluye el frontend compilado, FluidSynth y MuseScore. Aplicación disponible en `http://localhost:8000`.

## Notas de desarrollo

- En Mac con procesador Intel, PyTorch solo publica versiones hasta la 2.2.2, que funcionan con Python ≤ 3.12 (ver paso 1).
- Sin MuseScore todo funciona excepto la descarga de partituras; el servidor responde `503` con instrucciones de instalación.
- La transcripción funciona mejor con tempo estable (por ejemplo, grabaciones con metrónomo), porque permite cuantizar las notas a una cuadrícula. Las grabaciones con rubato producen partituras menos legibles.
- Los datos de contacto que aparecen en la interfaz se configuran en `web/src/project.ts`.

## Créditos y licencia

- Código: licencia [MIT](LICENSE). Basado en [MuScriptor](https://github.com/muscriptor/muscriptor) © 2026 Kyutai x Mirelo; modificaciones © 2026 Equipo EchoNotes.
- Pesos del modelo: publicados por MuScriptor en [HuggingFace](https://huggingface.co/MuScriptor) bajo [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (solo uso no comercial).
- SoundFont MuseScore General: distribuido bajo su propia licencia (MIT).
- Pista de ejemplo: "Headache" de Lost Deposit.

Artículo del modelo original:

```bibtex
@misc{rouard2026muscriptoropenmodelmultiinstrument,
      title={MuScriptor: An Open Model for Multi-Instrument Music Transcription},
      author={Simon Rouard and Michael Krause and Axel Roebel and Carl-Johann Simon-Gabriel and Alexandre Défossez},
      year={2026},
      eprint={2607.08168},
      archivePrefix={arXiv},
      primaryClass={cs.SD},
      url={https://arxiv.org/abs/2607.08168},
}
```
