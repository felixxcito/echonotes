import { UPSTREAM } from "../project";

const link =
  "text-accent underline underline-offset-4 opacity-90 hover:opacity-100";

export function Footer() {
  return (
    <footer className="mx-auto mt-4 flex max-w-7xl flex-wrap items-center justify-between gap-6 border-t border-line px-7 py-10 max-[760px]:flex-col max-[760px]:items-start">
      <p className="max-w-xl text-muted">
        EchoNotes es un sistema de transcripción musical automática para varios
        instrumentos: convierte audio en MIDI y partituras por instrumento.
        Basado en{" "}
        <a href={UPSTREAM.url} target="_blank" rel="noreferrer" className={link}>
          {UPSTREAM.name}
        </a>{" "}
        de {UPSTREAM.authors} (código MIT, pesos del modelo CC BY-NC 4.0).
      </p>
      <div className="flex items-center gap-3 text-sm text-faint">
        <img src="/echonotes-mark.svg" alt="" className="h-7 w-7" aria-hidden="true" />
        <span>
          <span className="font-serif text-base font-bold text-content">EchoNotes</span>
          {" · "}Sistemas de Información I
        </span>
      </div>
    </footer>
  );
}
