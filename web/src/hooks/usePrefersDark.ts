import { useEffect, useState } from "react";

const QUERY = "(prefers-color-scheme: dark)";

const getMedia = (): MediaQueryList | null =>
  typeof window !== "undefined" && typeof window.matchMedia === "function"
    ? window.matchMedia(QUERY)
    : null;

/** Tracks the OS light/dark preference. */
export function usePrefersDark(): boolean {
  const [dark, setDark] = useState(() => getMedia()?.matches ?? false);

  useEffect(() => {
    const media = getMedia();
    if (!media) return;
    const onChange = (e: MediaQueryListEvent) => setDark(e.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return dark;
}
