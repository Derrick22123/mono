export const zhTW = {
  appTitle: "Agent 聊天",
  emptyState: "開始對話吧！輸入訊息後按「傳送」。",
  composerPlaceholder: "輸入訊息…",
  send: "傳送",
  streaming: "助理正在回覆…",
  errors: {
    configMissing: "未設定 VITE_API_BASE_URL，無法連線至後端。",
    configEmpty: "VITE_API_BASE_URL 不可為空白。",
    healthDegraded: "後端尚未就緒，無法開始對話。",
    healthFetchFailed: "無法取得後端健康狀態。",
    network: "網路連線失敗，請稍後再試。",
    streamAbort: "回覆未完成",
    modelError: "模型回覆時發生錯誤。",
    credentialsMissing: "後端缺少 OPENAI_API_KEY。",
    generic: "發生未知錯誤。",
  },
  composer: {
    whitespaceOnly: "訊息不可為空白。",
    maxLength: "訊息不可超過 4000 字元。",
  },
} as const;

export type ErrorCode =
  | "CONFIG"
  | "HEALTH_DEGRADED"
  | "NETWORK"
  | "STREAM_ABORT"
  | "MODEL_ERROR";

export function getErrorMessage(code: ErrorCode, detail?: string): string {
  switch (code) {
    case "CONFIG":
      return detail ?? zhTW.errors.configMissing;
    case "HEALTH_DEGRADED":
      return detail ?? zhTW.errors.healthDegraded;
    case "NETWORK":
      return zhTW.errors.network;
    case "STREAM_ABORT":
      return zhTW.errors.streamAbort;
    case "MODEL_ERROR":
      return detail ?? zhTW.errors.modelError;
    default:
      return zhTW.errors.generic;
  }
}
