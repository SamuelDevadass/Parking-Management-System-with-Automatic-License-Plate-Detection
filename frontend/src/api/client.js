/*
  API CLIENT
  ==========
  Thin wrappers around fetch(). Every page imports { Api } from here instead
  of touching fetch() directly — same idea as your Tkinter code centralizing
  the psycopg connection string, just for HTTP instead of Postgres.

  Requests go to relative paths like "/api/wings". In dev, vite.config.js
  proxies "/api/*" to http://localhost:8000 (your FastAPI app), so there's
  no CORS to configure locally. In production you'd either serve both from
  the same origin, or set an env var here for an absolute backend URL.

  ENDPOINT CONTRACT — build these routes in FastAPI:
  ----------------------------------------------------
  GET  /api/wings                          -> ["A", "B", ...]
  GET  /api/wings/{wing}/centre             -> { centre_id: 1 }
  GET  /api/spots/availability?wing=A       -> { two_wheeler: 4, four_wheeler: 0 }
  POST /api/detection/start                 -> { ok: true }
  GET  /api/detection/status                -> { status: "running"|"done"|"idle", license_plate: "MH12AB1234" }
  POST /api/detection/stop                   -> { ok: true }
  GET  /api/vehicles/{license_plate}         -> { owner_id, model, colour, type, phone, name }
  POST /api/vehicles                         -> body: { owner_id, license_plate, model, colour, type, phone, name }
  GET  /api/spots?wing=A&centre_id=1&size=Two Wheeler -> [{ floor, spot_number, size }, ...]
  POST /api/entries                          -> body: { license_plate, centre_id, wing, floor, spot_number, folder_path }
  POST /api/exits                            -> body: { license_plate } -> { entry_time, exit_time, duration, amount }
  GET  /api/bills/{license_plate}/latest     -> { entry_time, exit_time, duration, amount, owner_name }
*/

async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${options.method || "GET"} ${path} failed (${res.status}): ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const Api = {
  getWings: () => request("/wings"),

  getCentreForWing: (wing) => request(`/wings/${encodeURIComponent(wing)}/centre`),

  getSpotAvailability: (wing) => request(`/spots/availability?wing=${encodeURIComponent(wing)}`),

  startDetection: () => request("/detection/start", { method: "POST" }),

  getDetectionStatus: () => request("/detection/status"),

  stopDetection: () => request("/detection/stop", { method: "POST" }),

  getVehicle: (licensePlate) => request(`/vehicles/${encodeURIComponent(licensePlate)}`),

  saveVehicle: (payload) =>
    request("/vehicles", { method: "POST", body: JSON.stringify(payload) }),

  getAvailableSpots: (wing, centreId, size) =>
    request(
      `/spots?wing=${encodeURIComponent(wing)}&centre_id=${encodeURIComponent(
        centreId
      )}&size=${encodeURIComponent(size)}`
    ),

  markEntry: (payload) => request("/entries", { method: "POST", body: JSON.stringify(payload) }),

  markExit: (licensePlate) =>
    request("/exits", { method: "POST", body: JSON.stringify({ license_plate: licensePlate }) }),

  getLatestBill: (licensePlate) => request(`/bills/${encodeURIComponent(licensePlate)}/latest`),
};
