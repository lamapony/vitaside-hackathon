/* VitaSide — demo transport layer.
 *
 * Wraps window.fetch so the dashboard always renders:
 *  - live-first: real /api/* calls pass through when the Python API is up.
 *  - mock-fallback: on network error or non-2xx, transparently return sample
 *    data from mockData.ts and flip demoMode on.
 *  - forceDemo: presenter can lock sample data (localStorage) so the pitch
 *    never depends on the backend being ready.
 *
 * One interception point covers every call site (getJson, postJson, the PUT
 * helper in MyContext, the skin-photo FormData POST) — no page edits needed.
 */
import { mockFor } from "./mockData";

const LS_KEY = "vitaside_force_demo";
const realFetch: typeof fetch = window.fetch.bind(window);

let installed = false;
let forceDemo = false;
let demoMode = false;
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((fn) => {
    try {
      fn();
    } catch {
      /* ignore listener errors */
    }
  });
}

function setDemoMode(v: boolean) {
  if (demoMode === v) return;
  demoMode = v;
  notify();
}

export function isDemoMode(): boolean {
  return demoMode || forceDemo;
}

export function isForceDemo(): boolean {
  return forceDemo;
}

export function subscribeDemoMode(fn: () => void): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

function persistForceDemo(v: boolean) {
  try {
    if (v) localStorage.setItem(LS_KEY, "1");
    else localStorage.removeItem(LS_KEY);
  } catch {
    /* localStorage may be unavailable */
  }
}

/** Lock sample data on (reliable for the pitch) or off (use live API). */
export function setForceDemo(v: boolean) {
  forceDemo = v;
  if (v) demoMode = true;
  persistForceDemo(v);
  notify();
}

function jsonRes(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function apiUrl(input: RequestInfo | URL): string | null {
  let url: string;
  if (typeof input === "string") url = input;
  else if (input instanceof URL) url = input.toString();
  else if (input && typeof input === "object" && "url" in input) url = (input as Request).url;
  else return null;
  return url.includes("/api/") ? url : null;
}

export function installDemoTransport() {
  if (installed) return;
  installed = true;
  const envLock = (import.meta.env as { VITE_DEMO_LOCK?: string }).VITE_DEMO_LOCK === "true";
  try {
    if (envLock || localStorage.getItem(LS_KEY) === "1") {
      forceDemo = true;
      demoMode = true;
    }
  } catch {
    /* ignore */
  }

  window.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = apiUrl(input);
    if (url === null) return realFetch(input as RequestInfo, init);

    const method = (init?.method ?? "GET").toUpperCase();

    // Locked demo: never touch the network.
    if (forceDemo) {
      const mock = mockFor(method, url, init?.body);
      return jsonRes(mock ?? {});
    }

    // Live-first.
    try {
      const res = await realFetch(input as RequestInfo, init);
      if (res.ok) return res;
      const mock = mockFor(method, url, init?.body);
      if (mock !== undefined) {
        setDemoMode(true);
        return jsonRes(mock);
      }
      return res;
    } catch (err) {
      const mock = mockFor(method, url, init?.body);
      if (mock !== undefined) {
        setDemoMode(true);
        return jsonRes(mock);
      }
      throw err;
    }
  }) as typeof fetch;
}
