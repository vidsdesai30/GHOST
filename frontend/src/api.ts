export type EventCategory = "observed" | "delayed" | "duplicate";

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
  stages: string[];
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
  node_type: "observed_event" | "predicted_action";
  label: string;
  event_id: string | null;
  predicted_action: string | null;
};

export type GraphEdge = {
  edge_id: string;
  source: string;
  target: string;
  relation: "ordered_sequence" | "supports_prediction";
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

type ScenarioRule = Scenario & {
  weights: Array<[string, number]>;
  events: SecurityEvent[];
};

const receivedAt = "2026-01-15T12:05:00.000Z";

const event = (
  scenarioId: string,
  id: string,
  minute: number,
  eventType: string,
  process: string,
  destination: string,
  sequence: number,
  attributes: Record<string, unknown>,
): SecurityEvent => ({
  event_id: id,
  timestamp: `2026-01-15T12:${String(minute).padStart(2, "0")}:00.000Z`,
  event_type: eventType,
  host: scenarioId === "scenario-office-macro" ? "workstation-07" : "build-node-02",
  process,
  user_account: "lab\\analyst",
  source: "synthetic-sensor",
  destination,
  attributes,
  scenario_id: scenarioId,
  ingestion: { received_at: receivedAt, source_batch: "fixture-a", sequence_number: sequence, is_duplicate: false, is_delayed: false },
});

const rules: ScenarioRule[] = [
  {
    scenario_id: "scenario-office-macro",
    name: "Office macro to credential access",
    description: "A document process launches a synthetic script chain and reaches a blocked credential access attempt.",
    status: "synthetic_demo",
    event_count: 4,
    stages: ["process_start", "network_connection", "script_execution", "credential_access_attempt", "credential_dump"],
    weights: [["credential_dump", 0.9], ["persistence_setup", 0.38]],
    events: [
      event("scenario-office-macro", "evt-001", 0, "process_start", "winword.exe", "-", 1, { parent_process: "explorer.exe", integrity: "medium" }),
      event("scenario-office-macro", "evt-002", 1, "network_connection", "winword.exe", "198.51.100.24:443", 2, { protocol: "https", bytes_out: 1842 }),
      event("scenario-office-macro", "evt-003", 3, "script_execution", "powershell.exe", "-", 3, { engine: "powershell", command_summary: "encoded payload (synthetic)" }),
      event("scenario-office-macro", "evt-004", 4, "credential_access_attempt", "powershell.exe", "lsass.exe", 4, { result: "blocked", sensor: "synthetic-edr" }),
    ],
  },
  {
    scenario_id: "scenario-build-runner",
    name: "Build runner persistence drift",
    description: "A synthetic build runner executes a script and reaches a scheduled-task setup hypothesis.",
    status: "synthetic_demo",
    event_count: 3,
    stages: ["process_start", "script_execution", "network_connection", "persistence_setup"],
    weights: [["persistence_setup", 0.82], ["credential_access_attempt", 0.31]],
    events: [
      event("scenario-build-runner", "evt-b01", 8, "process_start", "runner.exe", "-", 1, { parent_process: "service-host.exe", integrity: "high" }),
      event("scenario-build-runner", "evt-b02", 9, "script_execution", "pwsh.exe", "-", 2, { engine: "powershell", command_summary: "package bootstrap (synthetic)" }),
      event("scenario-build-runner", "evt-b03", 11, "network_connection", "pwsh.exe", "203.0.113.50:443", 3, { protocol: "https", bytes_out: 920 }),
    ],
  },
];

const cloneEvents = (items: SecurityEvent[]) => items.map((item) => ({
  ...item,
  attributes: { ...item.attributes },
  ingestion: { ...item.ingestion },
}));

function detect(rule: ScenarioRule, input: SecurityEvent[]): DetectionResult {
  const unique = new Map<string, SecurityEvent>();
  const duplicateIds: string[] = [];
  let outOfOrder = false;
  let previousTimestamp = "";
  input.forEach((item) => {
    if (unique.has(item.event_id)) duplicateIds.push(item.event_id);
    else unique.set(item.event_id, item);
    if (previousTimestamp && item.timestamp < previousTimestamp) outOfOrder = true;
    previousTimestamp = item.timestamp;
  });
  const normalized = [...unique.values()].sort((a, b) => a.timestamp.localeCompare(b.timestamp) || a.event_id.localeCompare(b.event_id));
  const delayedIds = normalized.filter((item) => item.ingestion.received_at > item.timestamp).map((item) => item.event_id);
  const stageEvents = new Map<string, SecurityEvent>();
  normalized.filter((item) => item.scenario_id === rule.scenario_id).forEach((item) => {
    if (rule.stages.includes(item.event_type) && !stageEvents.has(item.event_type)) stageEvents.set(item.event_type, item);
  });
  const observed = rule.stages.filter((stage) => stageEvents.has(stage));
  const missing = rule.stages.filter((stage) => !stageEvents.has(stage));
  const supportingIds = observed.map((stage) => stageEvents.get(stage)!.event_id);
  const predictions: Prediction[] = observed.length < 2 || missing.length === 0 ? [] : rule.weights.map(([action, weight]) => ({
    scenario_id: rule.scenario_id,
    predicted_action: action,
    confidence: Math.min(0.99, Math.round(weight * (0.55 + (observed.length / rule.stages.length) * 0.45) * 1000) / 1000),
    supporting_event_ids: supportingIds,
    observed_stages: observed,
    missing_expected_stages: missing,
    alternative_explanations: [
      "The sequence may be benign administrative activity with similar telemetry.",
      "A missing event may have occurred outside the synthetic sensor coverage.",
    ],
    reasoning: `Observed ${observed.length} of ${rule.stages.length} ordered stages; the next unmatched stage is ${missing[0]}.`,
  })).sort((a, b) => b.confidence - a.confidence || a.predicted_action.localeCompare(b.predicted_action));
  const nodes: GraphNode[] = normalized.filter((item) => item.scenario_id === rule.scenario_id).map((item) => ({
    node_id: `event:${item.event_id}`, node_type: "observed_event", label: item.event_type, event_id: item.event_id, predicted_action: null,
  }));
  const edges: GraphEdge[] = [];
  const observedNodes = observed.map((stage) => stageEvents.get(stage)!);
  observedNodes.slice(1).forEach((right, index) => {
    const left = observedNodes[index];
    edges.push({ edge_id: `edge:${left.event_id}:${right.event_id}`, source: `event:${left.event_id}`, target: `event:${right.event_id}`, relation: "ordered_sequence", inferred: true, supporting_event_ids: [left.event_id, right.event_id] });
  });
  predictions.forEach((prediction) => {
    const nodeId = `prediction:${prediction.predicted_action}`;
    nodes.push({ node_id: nodeId, node_type: "predicted_action", label: prediction.predicted_action, event_id: null, predicted_action: prediction.predicted_action });
    if (supportingIds.length) {
      const lastSupportingId = supportingIds[supportingIds.length - 1];
      edges.push({ edge_id: `edge:${lastSupportingId}:${nodeId}`, source: `event:${lastSupportingId}`, target: nodeId, relation: "supports_prediction", inferred: true, supporting_event_ids: supportingIds });
    }
  });
  return {
    scenario_id: rule.scenario_id,
    complete: missing.length === 0,
    insufficient_evidence: observed.length < 2,
    duplicate_event_ids: [...new Set(duplicateIds)],
    delayed_event_ids: delayedIds,
    out_of_order: outOfOrder,
    observed_stages: observed,
    missing_expected_stages: missing,
    predictions,
    graph_nodes: nodes,
    graph_edges: edges,
  };
}

export const scenarios = rules.map(({ weights: _weights, events: _events, ...scenario }) => scenario);

export const localResearch = {
  scenarios,
  events: (scenarioId: string) => cloneEvents(rules.find((rule) => rule.scenario_id === scenarioId)?.events ?? []),
  detect: (scenarioId: string, input?: SecurityEvent[]) => {
    const rule = rules.find((item) => item.scenario_id === scenarioId);
    if (!rule) throw new Error("Scenario not found");
    return detect(rule, input ? cloneEvents(input) : cloneEvents(rule.events));
  },
};
