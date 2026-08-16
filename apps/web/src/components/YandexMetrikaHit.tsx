import { useEffect } from "react";
import { useLocation } from "react-router-dom";

declare global {
  interface Window {
    ym?: (id: number, method: string, url?: string) => void;
  }
}

const METRIKA_ID = 111655649;

/** Send a Yandex.Metrika hit on client-side route changes. */
export function YandexMetrikaHit() {
  const location = useLocation();

  useEffect(() => {
    window.ym?.(METRIKA_ID, "hit", window.location.href);
  }, [location.pathname, location.search]);

  return null;
}
