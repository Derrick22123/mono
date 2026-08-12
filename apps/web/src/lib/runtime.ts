import { useMemo } from "react";
import { HttpAgent } from "@ag-ui/client";
import { useAgUiRuntime } from "@assistant-ui/react-ag-ui";
import type { ApiConfig } from "@/lib/config";
import { mapRuntimeError } from "@/lib/errors";
import type { AppError } from "@/lib/errors";

/**
 * AG-UI runtime sends the full ordered `messages[]` thread on each run (FR-004a).
 */
export function useChatRuntime(
  apiConfig: ApiConfig,
  onError: (error: AppError) => void,
) {
  const agent = useMemo(
    () =>
      new HttpAgent({
        url: apiConfig.aguiUrl,
      }),
    [apiConfig.aguiUrl],
  );

  return useAgUiRuntime({
    agent,
    onError: (error) => {
      onError(mapRuntimeError(error));
    },
    onCancel: () => {
      onError(mapRuntimeError(new DOMException("Aborted", "AbortError")));
    },
  });
}
