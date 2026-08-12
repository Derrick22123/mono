import { zhTW } from "@/i18n/zh-TW";
import type { ErrorCode } from "@/i18n/zh-TW";

export type AppError = {
  code: ErrorCode;
  message: string;
};

export function configErrorMessage(raw: string | undefined): AppError | null {
  if (raw === undefined) {
    return { code: "CONFIG", message: zhTW.errors.configMissing };
  }
  if (!raw.trim()) {
    return { code: "CONFIG", message: zhTW.errors.configEmpty };
  }
  return null;
}

export function healthErrorMessage(status: string, checks?: Record<string, string>): AppError | null {
  if (status === "healthy") {
    return null;
  }
  if (checks?.model_credentials === "missing") {
    return { code: "HEALTH_DEGRADED", message: zhTW.errors.credentialsMissing };
  }
  return { code: "HEALTH_DEGRADED", message: zhTW.errors.healthDegraded };
}

export function mapRuntimeError(error: unknown): AppError {
  if (error instanceof DOMException && error.name === "AbortError") {
    return { code: "STREAM_ABORT", message: zhTW.errors.streamAbort };
  }
  if (error instanceof TypeError) {
    return { code: "NETWORK", message: zhTW.errors.network };
  }
  if (error instanceof Error) {
    if (error.message.includes("503")) {
      return { code: "HEALTH_DEGRADED", message: zhTW.errors.credentialsMissing };
    }
    return { code: "MODEL_ERROR", message: error.message || zhTW.errors.modelError };
  }
  return { code: "MODEL_ERROR", message: zhTW.errors.generic };
}
