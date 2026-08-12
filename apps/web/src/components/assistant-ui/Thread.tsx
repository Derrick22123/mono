import {
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  useAuiState,
} from "@assistant-ui/react";
import { zhTW } from "@/i18n/zh-TW";
import { MAX_MESSAGE_LENGTH } from "@/lib/config";

type ChatComposerProps = {
  disabled?: boolean;
};

export function ChatComposer({ disabled = false }: ChatComposerProps) {
  return (
    <ComposerPrimitive.Root className="composer-root">
      <ComposerPrimitive.Input
        className="composer-input"
        placeholder={zhTW.composerPlaceholder}
        rows={2}
        maxLength={MAX_MESSAGE_LENGTH}
        disabled={disabled}
        aria-label={zhTW.composerPlaceholder}
      />
      <ComposerPrimitive.Send className="composer-send" disabled={disabled}>
        {zhTW.send}
      </ComposerPrimitive.Send>
      <p className="composer-hint">
        {zhTW.composer.maxLength} · {zhTW.composer.whitespaceOnly}
      </p>
    </ComposerPrimitive.Root>
  );
}

function UserMessage() {
  return (
    <MessagePrimitive.Root className="message message-user">
      <MessagePrimitive.Content />
    </MessagePrimitive.Root>
  );
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="message message-assistant">
      <MessagePrimitive.Content />
    </MessagePrimitive.Root>
  );
}

type ChatThreadProps = {
  composerDisabled?: boolean;
};

export function ChatThread({ composerDisabled = false }: ChatThreadProps) {
  const isRunning = useAuiState((state) => state.thread.isRunning);
  const disabled = composerDisabled || isRunning;

  return (
    <ThreadPrimitive.Root className="thread-root">
      <ThreadPrimitive.Viewport className="thread-viewport">
        <AuiIf condition={(state) => state.thread.isEmpty}>
          <p className="thread-empty">{zhTW.emptyState}</p>
        </AuiIf>

        <ThreadPrimitive.Messages
          components={{
            UserMessage,
            AssistantMessage,
          }}
        />

        <AuiIf condition={(state) => state.thread.isRunning}>
          <p className="streaming-indicator" aria-live="polite">
            {zhTW.streaming}
          </p>
        </AuiIf>

        <ThreadPrimitive.ViewportFooter>
          <ChatComposer disabled={disabled} />
        </ThreadPrimitive.ViewportFooter>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  );
}
