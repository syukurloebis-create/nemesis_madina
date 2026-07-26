export interface Metadata {
  tags: readonly string[];
  labels: Readonly<Record<string, string>>;
  annotations: Readonly<Record<string, unknown>>;
}