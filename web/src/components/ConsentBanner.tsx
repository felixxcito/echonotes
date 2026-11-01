import { useState } from "react";
import { Button } from "./Button";
import { analyticsAvailable, setConsent, storedConsent } from "../analytics";

/**
 * Bottom-of-page cookie consent bar: Google Analytics only ever loads after
 * an explicit "Accept", and the choice is remembered in localStorage. Renders
 * nothing in builds without a measurement ID (where there is no analytics to
 * consent to) or once a choice was made.
 */
export function ConsentBanner() {
  const [answered, setAnswered] = useState(
    () => !analyticsAvailable() || storedConsent() !== null,
  );
  if (answered) return null;

  const choose = (consent: boolean) => {
    setConsent(consent);
    setAnswered(true);
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-surface">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-6 gap-y-3 px-7 py-4">
        <p className="max-w-2xl text-sm text-muted">
          Usamos cookies (Google Analytics) para entender cómo se usa
          EchoNotes: visitas a la página y eventos de uso anónimos, por ejemplo
          la duración del audio transcrito y los instrumentos que eliges; nunca
          el audio en sí.
        </p>
        <div className="ml-auto flex gap-2.5">
          <Button onClick={() => choose(true)}>Aceptar</Button>
          <Button kind="secondaryOff" onClick={() => choose(false)}>
            Rechazar
          </Button>
        </div>
      </div>
    </div>
  );
}
