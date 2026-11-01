"""CLI de EchoNotes: transcripción de audio → MIDI."""

import dataclasses
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

import typer

from echonotes.events import NoteEndEvent, NoteStartEvent, ProgressEvent
from echonotes.tokenizer.mt3 import (
    MT3_FULL_PLUS_GROUP_NAMES,
    resolve_instrument_names,
)
from echonotes.transcription_model import TranscriptionModel
from echonotes.utils.beats import BeatDetectionError, TempoDetection
from echonotes.utils.download import ModelDownloadError
from echonotes.utils.sheets import (
    MuseScoreError,
    MuseScoreNotFoundError,
    find_musescore,
    prepare_output_dir,
    write_sheets,
)

app = typer.Typer(add_completion=False, help="EchoNotes — transcripción de audio a MIDI y partituras")


def _load_model(
    model_path: str | None, device: str | None, dtype: str | None = None
) -> TranscriptionModel:
    """load_model with CLI-friendly failure: known download problems (missing
    HuggingFace authentication, …) print a plain message instead of a traceback."""
    try:
        return TranscriptionModel.load_model(
            weights_path=model_path, device=device, dtype=dtype
        )
    except ModelDownloadError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


class OutputFormat(str, Enum):
    midi = "midi"
    json = "json"
    jsonl = "jsonl"
    sheets = "sheets"


def _transcribe(model, kwargs: dict, detect_tempo: str, quantize: bool = False):
    """transcribe_and_postprocess, with the CLI's --detect-tempo spelling and errors."""
    try:
        mode: TempoDetection = {
            "true": True,
            "false": False,
            "best-effort": "best-effort",
        }[detect_tempo]
        return model.transcribe_and_postprocess(
            **kwargs, detect_tempo=mode, quantize=quantize
        )
    except BeatDetectionError as e:
        typer.echo(f"Error: {e}", err=True)
        typer.echo("Usa --detect-tempo best-effort o false para continuar.", err=True)
        raise typer.Exit(1)


def _event_to_dict(ev: NoteStartEvent | NoteEndEvent) -> dict:
    if isinstance(ev, NoteStartEvent):
        return {"type": "start", **dataclasses.asdict(ev)}
    return {
        "type": "end",
        "end_time": ev.end_time,
        "start_event_index": ev.start_event_index,
    }


@app.command()
def transcribe(
    audio_file: Annotated[
        Path, typer.Argument(help="Archivo de audio de entrada (wav, mp3, flac, …)")
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help=(
                "Ruta del archivo de salida. Usa '-' para escribir en stdout (en ese "
                "caso el progreso y los tiempos se envían a stderr). "
                "Por defecto: <archivo_audio>.<ext>, con ext según --format. "
                "Con --format sheets es un directorio: debe estar vacío o no "
                "existir todavía, y se crea si falta."
            ),
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help=(
                "Formato de salida: midi (por defecto), json (un arreglo de eventos), "
                "jsonl (un evento por línea, emitido a medida que avanza la "
                "transcripción) o sheets (un directorio con partituras en PDF, "
                "MusicXML y MIDI; requiere tener MuseScore instalado)"
            ),
            case_sensitive=False,
        ),
    ] = OutputFormat.midi,
    notes: Annotated[
        bool, typer.Option("--notes", help="Imprime los eventos decodificados")
    ] = False,
    sampling: Annotated[
        bool,
        typer.Option(
            "--sampling", help="Usa muestreo con temperatura en lugar de decodificación voraz (greedy)"
        ),
    ] = False,
    temperature: Annotated[
        float,
        typer.Option(
            "--temperature", "-t", help="Temperatura de muestreo (solo con --sampling)"
        ),
    ] = 1.0,
    cfg_coef: Annotated[
        float, typer.Option("--cfg-coef", help="Coeficiente de classifier-free guidance")
    ] = 1.0,  # todo: make it dynamic
    model_path: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help=(
                "Tamaño del modelo ('small', 'medium', 'large'; por defecto: medium), "
                "una ruta local a un .safetensors o una URL hf:// / http(s)://"
            ),
        ),
    ] = None,
    device: Annotated[
        str,
        typer.Option(
            "--device", "-d", help="Dispositivo: 'auto', 'cpu', 'cuda', 'cuda:0', 'mps', …"
        ),
    ] = "auto",
    dtype: Annotated[
        str | None,
        typer.Option(
            "--dtype",
            help=(
                "Tipo de dato del transformer: 'float32', 'float16' o 'bfloat16'. "
                "Por defecto: float16 en MPS, float32 en los demás."
            ),
        ),
    ] = None,
    batch_size: Annotated[
        int | None,
        typer.Option(
            "--batch-size",
            "-b",
            help=(
                "Fragmentos generados por pasada (por defecto: 1; con "
                "--no-prelude-forcing: 4 en GPU, 1 en CPU). Valores > 1 bajan la "
                "calidad en los bordes de los fragmentos y requieren --no-prelude-forcing."
            ),
        ),
    ] = None,
    strict_eos: Annotated[
        bool,
        typer.Option(
            "--strict-eos",
            help="Lanza un error si un fragmento no emite EOS dentro del presupuesto de generación (por defecto: solo una advertencia)",
        ),
    ] = False,
    beam_size: Annotated[
        int,
        typer.Option(
            "--beam-size",
            help="Ancho del beam search (1 = greedy/muestreo, ≥2 activa beam search)",
        ),
    ] = 1,
    prelude_forcing: Annotated[
        bool,
        typer.Option(
            "--prelude-forcing/--no-prelude-forcing",
            help=(
                "Fuerza el prólogo de cada fragmento con las notas que siguen "
                "sonando del fragmento anterior, para que no reinicie con "
                "instrumentos equivocados. Necesita generar los fragmentos en "
                "orden, así que requiere --batch-size 1 (el valor por defecto)."
            ),
        ),
    ] = True,
    auralize: Annotated[
        Path | None,
        typer.Option(
            "--auralize",
            help=(
                "Escribe una auralización estéreo (I=audio original, D=síntesis MIDI) en "
                "esta ruta. Requiere fluidsynth en el PATH. La extensión define el "
                "formato: .wav (por defecto) o .mp3. Solo válido con --format midi."
            ),
        ),
    ] = None,
    soundfont: Annotated[
        Path | None,
        typer.Option(
            "--soundfont",
            help=(
                "Ruta a un SoundFont .sf2 para la auralización. Por defecto "
                "MuseScore_General.sf2, que se descarga una vez y se guarda en caché."
            ),
        ),
    ] = None,
    instruments: Annotated[
        str | None,
        typer.Option(
            "--instruments",
            help=(
                "Lista separada por comas de los grupos de instrumentos esperados. "
                "Si se indica, ningún instrumento fuera de la lista puede "
                "aparecer. No distingue mayúsculas; acepta abreviaturas no "
                "ambiguas (p. ej. 'timp,cello,dist'). Ejecuta "
                "'echonotes list-instruments' para ver todos los nombres."
            ),
        ),
    ] = None,
    # typer can't take the bool | Literal["best-effort"] union the API uses, so
    # the CLI spells all three states as strings and converts below.
    detect_tempo: Annotated[
        Literal["true", "false", "best-effort"],
        typer.Option(
            help=(
                "Detecta el tempo y el compás del audio y los escribe en el MIDI. "
                "'true' falla si no encuentra un tempo estable, 'best-effort' "
                "avisa y usa 120 BPM sin compás, 'false' omite la detección."
            ),
        ),
    ] = "best-effort",
) -> None:
    """Transcribe un archivo de audio a MIDI (o JSON, JSONL o partituras)."""
    instrument_names: list[str] | None = None
    if instruments is not None:
        tokens = [n for n in instruments.split(",") if n.strip()]
        try:
            instrument_names = resolve_instrument_names(tokens)
        except ValueError as e:
            typer.echo(
                f"Error: {e}. "
                "Ejecuta 'echonotes list-instruments' para ver los nombres disponibles.",
                err=True,
            )
            raise typer.Exit(1)
        typer.echo(f"Instrumentos: {', '.join(instrument_names)}", err=True)

    if not audio_file.exists():
        typer.echo(f"Error: no se encontró el archivo: {audio_file}", err=True)
        raise typer.Exit(1)

    if prelude_forcing and batch_size is not None and batch_size != 1:
        typer.echo(
            f"Error: --batch-size {batch_size} requiere --no-prelude-forcing: "
            "procesar por lotes desactiva el prelude forcing, lo que baja la "
            "calidad de la transcripción en los bordes de los fragmentos.",
            err=True,
        )
        raise typer.Exit(1)

    is_stdout = output is not None and str(output) == "-"

    if output is None:
        if format == OutputFormat.sheets:
            output = audio_file.parent / f"{audio_file.stem}_sheets"
        else:
            suffix = {
                OutputFormat.midi: ".mid",
                OutputFormat.json: ".json",
                OutputFormat.jsonl: ".jsonl",
            }[format]
            output = audio_file.with_suffix(suffix)

    if format == OutputFormat.sheets:
        if is_stdout:
            typer.echo(
                "Error: --format sheets escribe un directorio, así que no puede "
                "escribir en stdout. Indica la ruta de un directorio con -o.",
                err=True,
            )
            raise typer.Exit(1)
        # Both checked before the model loads: transcribing a song takes long
        # enough that discovering a missing MuseScore afterwards would sting.
        try:
            prepare_output_dir(output)
            find_musescore()
        except (ValueError, MuseScoreNotFoundError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    _device = None if device == "auto" else device

    # All chatty progress/timing info goes to stderr — stdout is reserved for
    # the actual output when `-o -` is used.
    typer.echo("Cargando modelo…", err=True)
    model = _load_model(model_path, _device, dtype)

    typer.echo(f"Transcribiendo {audio_file} …", err=True)

    if auralize is not None and format != OutputFormat.midi:
        typer.echo("Error: --auralize requiere --format midi", err=True)
        raise typer.Exit(1)

    kwargs = dict(
        audio=audio_file,
        use_sampling=sampling,
        temperature=temperature,
        cfg_coef=cfg_coef,
        instruments=instrument_names,
        batch_size=batch_size,
        no_eos_is_ok=not strict_eos,
        beam_size=beam_size,
        prelude_forcing=prelude_forcing,
    )

    if format == OutputFormat.sheets:
        # Quantize to get the "idealized" timing, otherwise we might get very weird
        # 1/64th rests etc.
        midi_bytes, grid = _transcribe(model, kwargs, detect_tempo, quantize=True)
        typer.echo(f"Generando partituras con MuseScore → {output} …", err=True)
        try:
            written = write_sheets(
                midi_bytes,
                output,
                quantized=grid is not None and grid.beat_subdivision is not None,
            )
        except MuseScoreError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
        for path in written:
            typer.echo(f"  {path.name}", err=True)
        typer.echo(f"Se guardaron {len(written)} archivos en {output}", err=True)
    elif format == OutputFormat.midi:
        midi_bytes, _ = _transcribe(model, kwargs, detect_tempo)
        if is_stdout:
            sys.stdout.buffer.write(midi_bytes)
            sys.stdout.buffer.flush()
        else:
            output.write_bytes(midi_bytes)
            typer.echo(f"MIDI guardado en {output}", err=True)
        if notes:
            typer.echo(
                "Vuelve a ejecutar con --format json para inspeccionar los eventos.", err=True
            )
        if auralize is not None and not is_stdout:
            from echonotes.utils.auralization import auralize as do_auralize

            typer.echo(f"Generando auralización → {auralize} …", err=True)
            do_auralize(
                midi_path=output,
                original_audio_path=audio_file,
                output_path=auralize,
                soundfont_path=soundfont,
            )
            typer.echo(f"Auralización guardada en {auralize}", err=True)
    elif format == OutputFormat.jsonl:
        # Stream one JSON object per line, flushing after each event so the
        # file (or stdout pipe) can be consumed live.
        if is_stdout:
            sink = sys.stdout
            close_after = False
        else:
            sink = output.open("w")
            close_after = True
        try:
            for e in model.transcribe(**kwargs):
                if isinstance(e, ProgressEvent):
                    continue
                sink.write(json.dumps(_event_to_dict(e)) + "\n")
                sink.flush()
                if notes:
                    typer.echo(str(e), err=True)
        finally:
            if close_after:
                sink.close()
        if not is_stdout:
            typer.echo(f"JSONL guardado en {output}", err=True)
    else:  # json
        events = [
            e for e in model.transcribe(**kwargs) if not isinstance(e, ProgressEvent)
        ]
        payload = json.dumps([_event_to_dict(e) for e in events], indent=2)
        if is_stdout:
            sys.stdout.write(payload + "\n")
            sys.stdout.flush()
        else:
            output.write_text(payload)
            typer.echo(f"JSON guardado en {output}", err=True)
        if notes:
            for e in events:
                typer.echo(str(e), err=True)


@app.command()
def serve(
    host: Annotated[str, typer.Option("--host", help="Dirección en la que escucha el servidor")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", help="Puerto en el que escucha el servidor")] = 8222,
    model_path: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help=(
                "Tamaño del modelo ('small', 'medium', 'large'; por defecto: medium), "
                "una ruta local a un .safetensors o una URL hf:// / http(s)://"
            ),
        ),
    ] = None,
    device: Annotated[
        str,
        typer.Option(
            "--device", "-d", help="Dispositivo: 'auto', 'cpu', 'cuda', 'cuda:0', 'mps', …"
        ),
    ] = "auto",
    dtype: Annotated[
        str | None,
        typer.Option(
            "--dtype",
            help=(
                "Tipo de dato del transformer: 'float32', 'float16' o 'bfloat16'. "
                "Por defecto: float16 en MPS, float32 en los demás."
            ),
        ),
    ] = None,
):
    """Inicia el servidor web de EchoNotes (interfaz + API; POST /transcribe → eventos SSE)."""
    import logging

    import uvicorn

    from echonotes.server import create_app

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )

    _device = None if device == "auto" else device
    typer.echo("Cargando modelo…")
    model = _load_model(model_path, _device, dtype)
    web_dir = Path(__file__).resolve().parent / "web_dist"
    fastapi_app = create_app(model, web_dir=web_dir if web_dir.is_dir() else None)
    uvicorn.run(fastapi_app, host=host, port=port)


@app.command()
def list_instruments():
    """Lista los nombres de grupos de instrumentos que acepta --instruments."""
    for name in MT3_FULL_PLUS_GROUP_NAMES:
        typer.echo(name)


def main():
    app()


if __name__ == "__main__":
    main()
