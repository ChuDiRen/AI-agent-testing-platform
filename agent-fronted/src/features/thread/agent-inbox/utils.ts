import { BaseMessage, isBaseMessage } from "@langchain/core/messages";
import { format } from "date-fns";
import { startCase } from "lodash";
import { HumanResponseWithEdits, SubmitType } from "./types";
import { HumanInterrupt } from "@langchain/langgraph/prebuilt";

export function prettifyText(action: string) {
  return startCase(action.replace(/_/g, " "));
}

export function isArrayOfMessages(
  value: Record<string, any>[],
): value is BaseMessage[] {
  if (
    value.every(isBaseMessage) ||
    (Array.isArray(value) &&
      value.every(
        (v) =>
          typeof v === "object" &&
          "id" in v &&
          "type" in v &&
          "content" in v &&
          "additional_kwargs" in v,
      ))
  ) {
    return true;
  }
  return false;
}

export function baseMessageObject(item: unknown): string {
  if (isBaseMessage(item)) {
    const contentText =
      typeof item.content === "string"
        ? item.content
        : JSON.stringify(item.content, null);
    let toolCallText = "";
    if ("tool_calls" in item) {
      toolCallText = JSON.stringify(item.tool_calls, null);
    }
    if ("type" in item) {
      return `${item.type}:${contentText ? ` ${contentText}` : ""}${toolCallText ? ` - Tool calls: ${toolCallText}` : ""}`;
    } else if ("_getType" in item) {
      return `${item._getType()}:${contentText ? ` ${contentText}` : ""}${toolCallText ? ` - Tool calls: ${toolCallText}` : ""}`;
    }
  } else if (
    typeof item === "object" &&
    item &&
    "type" in item &&
    "content" in item
  ) {
    const contentText =
      typeof item.content === "string"
        ? item.content
        : JSON.stringify(item.content, null);
    let toolCallText = "";
    if ("tool_calls" in item) {
      toolCallText = JSON.stringify(item.tool_calls, null);
    }
    return `${item.type}:${contentText ? ` ${contentText}` : ""}${toolCallText ? ` - Tool calls: ${toolCallText}` : ""}`;
  }

  if (typeof item === "object") {
    return JSON.stringify(item, null);
  } else {
    return item as string;
  }
}

export function unknownToPrettyDate(input: unknown): string | undefined {
  try {
    if (
      Object.prototype.toString.call(input) === "[object Date]" ||
      new Date(input as string)
    ) {
      return format(new Date(input as string), "MM/dd/yyyy hh:mm a");
    }
  } catch (_) {
    // failed to parse date. no-op
  }
  return undefined;
}

export function createDefaultHumanResponse(
  interrupt: HumanInterrupt,
  initialHumanInterruptEditValue: React.MutableRefObject<
    Record<string, string>
  >,
): {
  responses: HumanResponseWithEdits[];
  defaultSubmitType: SubmitType | undefined;
  hasAccept: boolean;
} {
  const responses: HumanResponseWithEdits[] = [];

  // Only support modern middleware shape
  const anyInt: any = interrupt as any;
  const firstActionRaw =
    Array.isArray(anyInt.action_requests) && anyInt.action_requests.length > 0
      ? anyInt.action_requests[0]
      : undefined;
  const firstAction = firstActionRaw
    ? {
      action: firstActionRaw.name ?? firstActionRaw.action,
      args: firstActionRaw.args ?? {},
    }
    : undefined;

  const decisions: string[] = Array.isArray(anyInt.review_configs)
    ? (anyInt.review_configs[0]?.allowed_decisions ?? [])
    : [];

  const cfg = {
    allow_accept: decisions.includes("approve") || decisions.includes("accept"),
    allow_edit: decisions.includes("edit"),
    allow_ignore: decisions.includes("reject") || decisions.includes("ignore"),
    allow_respond: decisions.includes("respond") || decisions.includes("response"),
  };

  // Populate editable initial values when edit+accept are allowed
  if (cfg.allow_edit && firstAction?.args) {
    if (cfg.allow_accept) {
      Object.entries(firstAction.args).forEach(([k, v]) => {
        let stringValue = "";
        if (typeof v === "string") {
          stringValue = v;
        } else {
          try {
            stringValue = JSON.stringify(v, null);
          } catch {
            stringValue = String(v);
          }
        }

        if (
          !initialHumanInterruptEditValue.current ||
          !(k in initialHumanInterruptEditValue.current)
        ) {
          initialHumanInterruptEditValue.current = {
            ...initialHumanInterruptEditValue.current,
            [k]: stringValue,
          };
        } else if (
          k in initialHumanInterruptEditValue.current &&
          initialHumanInterruptEditValue.current[k] !== stringValue
        ) {
          console.error(
            "KEY AND VALUE FOUND IN initialHumanInterruptEditValue.current THAT DOES NOT MATCH THE ACTION REQUEST",
            {
              key: k,
              value: stringValue,
              expectedValue: initialHumanInterruptEditValue.current[k],
            },
          );
        }
      });
      responses.push({ type: "edit", args: { ...firstAction }, acceptAllowed: true, editsMade: false });
    } else {
      responses.push({ type: "edit", args: { ...firstAction }, acceptAllowed: false });
    }
  }

  if (cfg.allow_ignore) {
    responses.push({ type: "ignore", args: "" });
  }

  // Determine default submit type by priority
  const hasAccept = responses.find((r) => r.acceptAllowed) || cfg.allow_accept;
  const hasEdit = responses.find((r) => r.type === "edit");

  let defaultSubmitType: SubmitType | undefined;
  if (hasAccept) defaultSubmitType = "accept";
  else if (hasEdit) defaultSubmitType = "edit";

  // Ensure presence of explicit accept/ignore options if allowed
  if (cfg.allow_accept && !responses.find((r) => r.type === "accept")) {
    responses.push({ type: "accept", args: null });
  }
  if (cfg.allow_ignore && !responses.find((r) => r.type === "ignore")) {
    responses.push({ type: "ignore", args: null });
  }

  return { responses, defaultSubmitType, hasAccept: !!hasAccept };
}

export function constructOpenInStudioURL(
  deploymentUrl: string,
  threadId?: string,
) {
  const smithStudioURL = new URL("https://smith.langchain.com/studio/thread");
  // trim the trailing slash from deploymentUrl
  const trimmedDeploymentUrl = deploymentUrl.replace(/\/$/, "");

  if (threadId) {
    smithStudioURL.pathname += `/${threadId}`;
  }

  smithStudioURL.searchParams.append("baseUrl", trimmedDeploymentUrl);

  return smithStudioURL.toString();
}

export function haveArgsChanged(
  args: unknown,
  initialValues: Record<string, string>,
): boolean {
  if (typeof args !== "object" || !args) {
    return false;
  }

  const currentValues = args as Record<string, string>;

  return Object.entries(currentValues).some(([key, value]) => {
    const valueString = ["string", "number"].includes(typeof value)
      ? value.toString()
      : JSON.stringify(value, null);
    return initialValues[key] !== valueString;
  });
}
