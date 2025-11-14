import { HumanInterrupt } from "@langchain/langgraph/prebuilt";

export function isAgentInboxInterruptSchema(
  value: unknown,
): value is HumanInterrupt | HumanInterrupt[] {
  const obj: any = Array.isArray(value) ? (value as any[])[0] : (value as any);
  if (!obj || typeof obj !== "object") return false;

  // Only support newer middleware shape: { action_requests: [...], review_configs: [...] }
  const modernOk =
    Array.isArray(obj.action_requests) &&
    obj.action_requests.length > 0 &&
    Array.isArray(obj.review_configs) &&
    obj.review_configs.length > 0;

  return modernOk;
}
