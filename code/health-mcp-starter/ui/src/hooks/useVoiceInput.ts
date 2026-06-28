/* VitaSide — voice input hook (Web Speech API).
 *
 * Browser speech recognition for note dictation. Note: most Chromium browsers
 * process audio via the browser vendor's speech service (network). The UI flags
 * this so the local-first promise stays honest. A fully on-device model is a
 * future option; for now this gives accessible hands-free capture.
 */
import { useCallback, useEffect, useRef, useState } from "react";

/* eslint-disable @typescript-eslint/no-explicit-any */
type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: (event: any) => void;
  onerror: (event: any) => void;
  onend: () => void;
};

function getRecognitionCtor(): (new () => SpeechRecognitionLike) | null {
  if (typeof window === "undefined") return null;
  const w = window as any;
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

export type VoiceInput = {
  supported: boolean;
  listening: boolean;
  interim: string;
  transcript: string;
  setTranscript: (v: string) => void;
  start: () => void;
  stop: () => void;
  reset: () => void;
  error: string | null;
};

export function useVoiceInput(lang = "en-US"): VoiceInput {
  const [supported] = useState(() => !!getRecognitionCtor());
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recRef = useRef<SpeechRecognitionLike | null>(null);
  const wantRef = useRef(false);

  const stop = useCallback(() => {
    wantRef.current = false;
    setListening(false);
    setInterim("");
    try { recRef.current?.stop(); } catch { /* ignore */ }
  }, []);

  const start = useCallback(() => {
    const Ctor = getRecognitionCtor();
    if (!Ctor) {
      setError("Voice input is not supported in this browser. Try Chrome or Edge.");
      return;
    }
    setError(null);
    wantRef.current = true;
    const rec = new Ctor();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = lang;
    rec.onresult = (event: any) => {
      let interimText = "";
      let finalText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const r = event.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interimText += r[0].transcript;
      }
      if (finalText) {
        const clean = finalText.trim();
        setTranscript((prev) => (prev ? `${prev} ${clean}` : clean));
      }
      setInterim(interimText);
    };
    rec.onerror = (event: any) => {
      setError(event?.error ? `Voice input error: ${event.error}` : "Voice input error");
      wantRef.current = false;
      setListening(false);
    };
    rec.onend = () => {
      if (wantRef.current) {
        try { rec.start(); } catch { /* restart after timeout */ }
      } else {
        setListening(false);
      }
    };
    recRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch {
      setError("Could not start voice input. Check microphone permissions.");
      setListening(false);
    }
  }, [lang]);

  const reset = useCallback(() => {
    setTranscript("");
    setInterim("");
    setError(null);
  }, []);

  useEffect(
    () => () => {
      wantRef.current = false;
      try { recRef.current?.abort(); } catch { /* ignore */ }
    },
    []
  );

  return { supported, listening, interim, transcript, setTranscript, start, stop, reset, error };
}
