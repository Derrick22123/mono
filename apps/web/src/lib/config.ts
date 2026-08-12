const MAX_MESSAGE_LENGTH = 4000;

export type ApiConfig = {
  baseUrl: string;
  aguiUrl: string;
  healthUrl: string;
};

export function readApiConfig(): { config: ApiConfig | null; error: string | null } {
  const raw = import.meta.env.VITE_API_BASE_URL;
  if (raw === undefined) {
    return { config: null, error: "missing" };
  }
  const trimmed = raw.trim();
  if (!trimmed) {
    return { config: null, error: "empty" };
  }
  const baseUrl = trimmed.replace(/\/+$/, "");
  return {
    config: {
      baseUrl,
      aguiUrl: `${baseUrl}/agui`,
      healthUrl: `${baseUrl}/v1/health`,
    },
    error: null,
  };
}

export { MAX_MESSAGE_LENGTH };
