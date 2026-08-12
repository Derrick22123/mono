import { zhTW } from "@/i18n/zh-TW";

type ConfigErrorProps = {
  message: string;
};

export function ConfigError({ message }: ConfigErrorProps) {
  return (
    <div className="config-error" role="alert">
      <h2>{zhTW.appTitle}</h2>
      <p>{message}</p>
    </div>
  );
}
