/**
 * Frontend API client — calls the Python FastAPI backend & Flask Camera service.
 * Configured via environment variables:
 * - NEXT_PUBLIC_API_URL: Python FastAPI backend (default http://localhost:8000)
 * - NEXT_PUBLIC_CAMERA_BACKEND_URL: Python Flask USB Webcam service (default http://localhost:5001)
 */

export const FASTAPI_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000";

export const CAMERA_BASE_URL =
  process.env.NEXT_PUBLIC_CAMERA_BACKEND_URL ??
  "http://localhost:5001";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${FASTAPI_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

async function cameraFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${CAMERA_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let errorDetail = "";
    try {
      const errJson = await res.json();
      errorDetail = errJson.message || errJson.details || errJson.error || JSON.stringify(errJson);
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(`Camera Service (${res.status}): ${errorDetail}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface CandidatePrediction {
  disease_class: string;
  display_name: string;
  confidence: number;
  confidence_percentage: number;
}

export interface PredictionResult {
  predicted_class: string;
  disease_label: string;
  confidence: number;
  confidence_percentage: number;
  status: "confirmed" | "low_confidence" | "uncertain" | "no_plant";
  is_healthy: boolean;
  top_predictions: CandidatePrediction[];
  recommended_action: string;
  recommendations?: {
    immediate: string[];
    preventive: string[];
    disclaimer: string;
  };
  processing_time_ms: number;
  image_metadata: {
    width: number;
    height: number;
    format: string;
    size_kb: number;
  };
  model_version: string;
}

export interface CameraStatus {
  running: boolean;
  initialized: boolean;
  device_index: number;
  requested_resolution: string;
  actual_resolution: string;
  requested_fps: number;
  actual_fps: number;
  backend: string;
  frame_count: number;
  active_clients: number;
  last_frame_timestamp: number;
  last_frame_age_seconds: number | null;
  error_message: string | null;
}

export interface CameraHealth {
  status: string;
  service: string;
  version: string;
  camera_initialized: boolean;
  camera_running: boolean;
  device_index: number;
  error: string | null;
}

// ── AI Prediction API ─────────────────────────────────────────────────────────
export const predictApi = {
  predictFile: async (fileOrBlob: File | Blob, filename: string = "capture.jpg"): Promise<PredictionResult> => {
    const formData = new FormData();
    formData.append("file", fileOrBlob, filename);

    const res = await fetch(`${FASTAPI_BASE_URL}/api/predict`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      let msg = "";
      try {
        const errJson = await res.json();
        msg = errJson.detail || JSON.stringify(errJson);
      } catch {
        msg = await res.text();
      }
      throw new Error(`Inference Error (${res.status}): ${msg}`);
    }
    return res.json() as Promise<PredictionResult>;
  },

  predictBase64: async (base64String: string): Promise<PredictionResult> => {
    const res = await fetch(`${FASTAPI_BASE_URL}/api/predict/base64`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64: base64String }),
    });
    if (!res.ok) {
      let msg = "";
      try {
        const errJson = await res.json();
        msg = errJson.detail || JSON.stringify(errJson);
      } catch {
        msg = await res.text();
      }
      throw new Error(`Inference Error (${res.status}): ${msg}`);
    }
    return res.json() as Promise<PredictionResult>;
  },
};

// ── Raspberry Pi 5 USB Webcam API ─────────────────────────────────────────────
export const cameraApi = {
  getHealth: () => cameraFetch<CameraHealth>("/health"),
  getStatus: () => cameraFetch<CameraStatus>("/camera/status"),
  start: () =>
    cameraFetch<{ success: boolean; message: string; status: CameraStatus }>("/camera/start", {
      method: "POST",
    }),
  stop: () =>
    cameraFetch<{ success: boolean; message: string; status: CameraStatus }>("/camera/stop", {
      method: "POST",
    }),
  getVideoStreamUrl: () => `${CAMERA_BASE_URL}/video`,
  getSnapshotUrl: () => `${CAMERA_BASE_URL}/snapshot`,
  fetchSnapshotBlob: async (): Promise<Blob> => {
    const res = await fetch(`${CAMERA_BASE_URL}/snapshot`, {
      method: "GET",
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Failed to capture snapshot from camera service: ${res.statusText}`);
    }
    return res.blob();
  },
};

// ── Detections ────────────────────────────────────────────────────────────────
export const detectionsApi = {
  getAll: () => apiFetch<{ latest: unknown; history: unknown[]; total: number }>("/api/detections"),
  getLatest: () => apiFetch<unknown>("/api/detections/latest"),
  getTrends: () => apiFetch<{ trend_data: unknown[]; disease_distribution: unknown[] }>("/api/detections/trends"),
  getById: (id: string) => apiFetch<unknown>(`/api/detections/${id}`),
};

// ── Sensors ───────────────────────────────────────────────────────────────────
export const sensorsApi = {
  getCurrent: () =>
    apiFetch<{
      temperature_celsius: number;
      humidity_percentage: number;
      soil_moisture_percentage: number;
      light_intensity_lux: number;
      updated_at: string;
    }>("/api/sensors"),
};

// ── Farm ──────────────────────────────────────────────────────────────────────
export const farmApi = {
  getGrid: () => apiFetch<unknown>("/api/farm/grid"),
  getCell: (row: number, section: string) => apiFetch<unknown>(`/api/farm/grid/${row}/${section}`),
  getSummary: () => apiFetch<unknown>("/api/farm/summary"),
  getDiseaseInfo: (diseaseClass: string) => apiFetch<unknown>(`/api/farm/disease-info/${diseaseClass}`),
};

// ── Chat ──────────────────────────────────────────────────────────────────────
export const chatApi = {
  sendMessage: (message: string) =>
    apiFetch<{ response: string; context_used: string }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  getSuggestions: () => apiFetch<{ suggestions: string[] }>("/api/chat/suggestions"),
};

// ── Health ────────────────────────────────────────────────────────────────────
export const healthApi = {
  check: () => apiFetch<{ status: string; version: string }>("/health"),
};
