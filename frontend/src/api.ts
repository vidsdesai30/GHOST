export type IngestionMetadata = {
  received_at: string;
  source_batch: string;
  sequence_number: number | null;
  is_duplicate: boolean;
  is_delayed: boolean;
};

export type SecurityEvent = {
  event_id: string;
  timestamp: string;
  event_type: string;
  host: string;
  process: string | null;
  user_account: string | null;
  source: string | null;
  destination: string | null;
  attributes: Record<string, unknown>;
  scenario_id: string;
  ingestion: IngestionMetadata;
};

export type Scenario = {
  scenario_id: string;
  name: string;
  description: string;
  status: string;
  event_count: number;
};

export type Prediction = {
  scenario_id: string;
  predicted_action: string;
  confidence: number;
  supporting_event_ids: string[];
  observed_stages: string[];
  missing_expected_stages: string[];
  alternative_explanations: string[];
  reasoning: string;
};

export type GraphNode = {
  node_id: string;
  node_type: "observed_event" | "predicted_action" | string;
  label: string;
  event_id: string | null;
  predicted_action: string | null;
};

export type GraphEdge = {
  edge_id: string;
  source: string;
  target: string;
  relation: string;
  inferred: boolean;
  supporting_event_ids: string[];
};

export type DetectionResult = {
  scenario_id: string;
  complete: boolean;
  insufficient_evidence: boolean;
  duplicate_event_ids: string[];
  delayed_event_ids: string[];
  out_of_order: boolean;
  observed_stages: string[];
  missing_expected_stages: string[];
  predictions: Prediction[];
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
};

export type ApiStatus = {
  status: string;
  stored_events: number;
  database: string;
};

const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Preserve a sanitized status-only error when the server response is not JSON.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string }>("/api/health"),
  status: () => request<ApiStatus>("/api/status"),
  scenarios: () => request<Scenario[]>("/api/scenarios"),
  events: (scenarioId: string) => request<SecurityEvent[]>(`/api/events?scenario_id=${encodeURIComponent(scenarioId)}`),
  demoEvents: (scenarioId: string) => request<SecurityEvent[]>(`/api/scenarios/${encodeURIComponent(scenarioId)}/demo-events`),
  detect: (scenarioId: string, events: SecurityEvent[]) => request<DetectionResult>("/api/detection", {
    method: "POST",
    body: JSON.stringify({ scenario_id: scenarioId, events }),
  }),
  graph: (scenarioId: string) => request<DetectionResult>(`/api/graph/${encodeURIComponent(scenarioId)}`),
};
