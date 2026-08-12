import { useEffect, useMemo, useState } from "react";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { ConfigError } from "@/components/ConfigError";
import { ChatThread } from "@/components/assistant-ui";
import { readApiConfig } from "@/lib/config";
import { healthErrorMessage, type AppError } from "@/lib/errors";
import { useChatRuntime } from "@/lib/runtime";
import { zhTW } from "@/i18n/zh-TW";

function RuntimeShell({
  apiBaseUrl,
  healthUrl,
}: {
  apiBaseUrl: string;
  healthUrl: string;
}) {
  const [runtimeError, setRuntimeError] = useState<AppError | null>(null);
  const [healthError, setHealthError] = useState<AppError | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  const apiConfig = useMemo(
    () => ({
      baseUrl: apiBaseUrl,
      aguiUrl: `${apiBaseUrl}/agui`,
      healthUrl,
    }),
    [apiBaseUrl, healthUrl],
  );

  useEffect(() => {
    let cancelled = false;
    async function checkHealth() {
      setHealthLoading(true);
      try {
        const response = await fetch(healthUrl);
        if (!response.ok) {
          throw new Error(`health status ${response.status}`);
        }
        const payload = (await response.json()) as {
          status: string;
          checks?: Record<string, string>;
        };
        if (!cancelled) {
          setHealthError(healthErrorMessage(payload.status, payload.checks));
        }
      } catch {
        if (!cancelled) {
          setHealthError({
            code: "HEALTH_DEGRADED",
            message: zhTW.errors.healthFetchFailed,
          });
        }
      } finally {
        if (!cancelled) {
          setHealthLoading(false);
        }
      }
    }
    void checkHealth();
    return () => {
      cancelled = true;
    };
  }, [healthUrl]);

  const runtime = useChatRuntime(apiConfig, setRuntimeError);
  const blockingError = healthError ?? runtimeError;
  const composerDisabled = healthLoading || Boolean(blockingError);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="chat-panel">
        {blockingError && (
          <div className="error-banner" role="alert">
            {blockingError.message}
          </div>
        )}
        <ChatThread composerDisabled={composerDisabled} />
      </div>
    </AssistantRuntimeProvider>
  );
}

export default function App() {
  const { config, error } = readApiConfig();

  if (error === "missing") {
    return (
      <div className="app-shell">
        <header className="app-header">
          <h1>{zhTW.appTitle}</h1>
        </header>
        <main className="app-main">
          <ConfigError message={zhTW.errors.configMissing} />
        </main>
      </div>
    );
  }

  if (error === "empty" || !config) {
    return (
      <div className="app-shell">
        <header className="app-header">
          <h1>{zhTW.appTitle}</h1>
        </header>
        <main className="app-main">
          <ConfigError message={zhTW.errors.configEmpty} />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>{zhTW.appTitle}</h1>
      </header>
      <main className="app-main">
        <RuntimeShell apiBaseUrl={config.baseUrl} healthUrl={config.healthUrl} />
      </main>
    </div>
  );
}
