/**
 * FAQ below the welcome screen. Mostly for SEO: the questions are the phrasings
 * people actually search for, and native <details> keeps collapsed answers in
 * the DOM where crawlers still see them — that's where the value is.
 *
 * The FAQPage JSON-LD is a bonus, not the point: Google stopped showing FAQ
 * rich results for general sites in 2023 (government/health domains only), so
 * it buys nothing there. Other engines and AI crawlers still read it, and it's
 * generated from the same strings, so it costs ~8 lines and can't go stale.
 */

import { track } from "../analytics";

/** Answers are single strings with `[label](href)` links and `code` spans
 *  inline, so the visible copy and the JSON-LD can't drift: both are rendered
 *  from the same text (see `renderAnswer` / `plainText`). */
const QA: { q: string; a: string }[] = [
  {
    q: "¿Qué es EchoNotes?",
    a: "EchoNotes convierte música en MIDI y partituras: le das una grabación y transcribe las notas que toca cada instrumento.",
  },
  {
    q: "¿Es gratis?",
    a: "Sí. El código es de licencia MIT y los pesos del modelo se publican bajo licencia CC BY-NC 4.0, es decir, solo para uso no comercial.",
  },
  {
    q: "¿Qué formatos de audio puedo subir?",
    a: "MP3, WAV, FLAC, OGG, M4A, AIFF u Opus. Arrastra el archivo a la página o usa el botón para seleccionarlo.",
  },
  {
    q: "¿Qué instrumentos puede transcribir?",
    a: "Voz, piano, guitarras, bajo, cuerdas, metales, maderas, batería y muchos más. Para mejorar la precisión puedes indicar de antemano qué instrumentos esperas; la lista completa está en el selector de instrumentos.",
  },
  {
    q: "¿Puedo convertir una canción en partitura?",
    a: "Sí. Después de transcribir, el menú de descarga ofrece las partituras en PDF, por instrumento o la partitura completa. También obtienes el archivo MusicXML para editarlo en programas como MuseScore, Sibelius o Guitar Pro.",
  },
  {
    q: "¿Genera tablaturas de guitarra?",
    a: "Sí. Los instrumentos con trastes, como la guitarra y el bajo, también generan una tablatura en PDF junto a la notación estándar. No escribe cifrado de acordes, solo las notas que realmente se tocan.",
  },
  {
    q: "¿Puedo usarlo desde la terminal o desde Python?",
    a: "Sí. `uv run echonotes serve` levanta esta misma interfaz en tu equipo, `uv run echonotes transcribe cancion.mp3` transcribe desde la línea de comandos, y la API de Python se usa en un par de líneas. Funciona con GPU NVIDIA, con Apple Silicon (Metal) y en CPU con el modelo pequeño. Las instrucciones están en el README del proyecto.",
  },
  {
    q: "¿Qué tan preciso es?",
    a: "El modelo en el que se basa es uno de los modelos abiertos de transcripción más precisos, pero no es perfecto: es un muy buen punto de partida que luego puedes pulir en un editor o DAW. Funciona mejor con música acústica y de guitarra que con música electrónica. Los resultados detallados están en el [artículo científico](https://arxiv.org/abs/2607.08168).",
  },
  {
    q: "¿Qué pasa con el audio que subo?",
    a: "Se transcribe en el servidor donde corre EchoNotes y no se guarda después. Si ejecutas EchoNotes en tu propio equipo, el audio nunca sale de él.",
  },
  {
    q: "¿Cómo funciona técnicamente?",
    a: "Es un transformer de tipo decoder-only que lee el audio en fragmentos de 5 segundos y genera una secuencia de tokens que describen el inicio y el final de cada nota y su instrumento; esa secuencia se ensambla luego en un archivo MIDI. El modelo original se entrenó con 170 mil canciones, desde música clásica hasta heavy metal. [Más detalles en el artículo](https://arxiv.org/abs/2607.08168).",
  },
  {
    q: "¿Cómo reporto un error o envío comentarios?",
    a: "Escríbele al equipo de EchoNotes; los datos de contacto están en el README del proyecto.",
  },
];

/** `[label](href)` or `code`. */
const TOKEN = /\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`/g;

/** Answer text → React nodes, with the two inline forms above marked up. */
function renderAnswer(a: string) {
  const out = [];
  let last = 0;
  for (const m of a.matchAll(TOKEN)) {
    if (m.index > last) out.push(a.slice(last, m.index));
    out.push(
      m[1] ? (
        <a
          key={m.index}
          href={m[2]}
          target="_blank"
          rel="noreferrer"
          className="text-accent underline underline-offset-4"
        >
          {m[1]}
        </a>
      ) : (
        <code key={m.index} className="font-mono text-[0.9em] text-content">
          {m[3]}
        </code>
      ),
    );
    last = m.index + m[0].length;
  }
  out.push(a.slice(last));
  return out;
}

/** Same text with the markup stripped, for the JSON-LD. */
const plainText = (a: string) =>
  a.replace(TOKEN, (_m, label, _href, code) => label ?? code);

export function Faq() {
  return (
    <section className="mx-auto max-w-3xl px-7 pb-16">
      <h2 className="mb-4 font-serif text-3xl font-bold leading-none text-content">
        Preguntas frecuentes
      </h2>
      <div className="border-t border-line">
        {QA.map(({ q, a }) => (
          <details
            key={q}
            className="group border-b border-line"
            onToggle={(e) => {
              if (e.currentTarget.open) track("faq_open", { question: q });
            }}
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-4 text-base font-semibold text-content marker:content-none hover:text-accent">
              <h3 className="m-0 text-base font-semibold">{q}</h3>
              <span
                className="shrink-0 text-muted transition-transform group-open:rotate-90"
                aria-hidden="true"
              >
                ›
              </span>
            </summary>
            <p className="m-0 pb-4 pr-8 text-base leading-relaxed text-muted">
              {renderAnswer(a)}
            </p>
          </details>
        ))}
      </div>
      <script
        type="application/ld+json"
        // Static, locally-authored strings — no user input reaches this.
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: QA.map(({ q, a }) => ({
              "@type": "Question",
              name: q,
              acceptedAnswer: { "@type": "Answer", text: plainText(a) },
            })),
          }),
        }}
      />
    </section>
  );
}
