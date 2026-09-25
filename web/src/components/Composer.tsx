import { useState } from "react";
import { Button, Textarea, makeStyles, tokens } from "@fluentui/react-components";
import { SendRegular } from "@fluentui/react-icons";

const useStyles = makeStyles({
  root: { display: "flex", gap: tokens.spacingHorizontalS, alignItems: "flex-end" },
  input: { flexGrow: 1 },
});

interface Props {
  disabled: boolean;
  onSend: (text: string) => void;
}

/** Message input. Enter sends; Shift+Enter adds a new line. */
export function Composer({ disabled, onSend }: Props) {
  const styles = useStyles();
  const [text, setText] = useState("");

  const submit = () => {
    if (disabled || !text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <form
      className={styles.root}
      aria-label="Send a message"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <Textarea
        className={styles.input}
        aria-label="Your message"
        placeholder="Ask about plans, billing, orders, or service status…"
        value={text}
        disabled={disabled}
        resize="vertical"
        maxLength={2000}
        onChange={(_, data) => setText(data.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
      />
      <Button
        type="submit"
        appearance="primary"
        icon={<SendRegular />}
        disabled={disabled || !text.trim()}
      >
        Send
      </Button>
    </form>
  );
}
