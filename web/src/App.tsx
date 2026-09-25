import { useEffect, useRef, useState } from "react";
import {
  Body1,
  Button,
  Caption1,
  FluentProvider,
  MessageBar,
  MessageBarActions,
  MessageBarBody,
  MessageBarTitle,
  Title3,
  makeStyles,
  tokens,
  webDarkTheme,
  webLightTheme,
} from "@fluentui/react-components";
import { PanelRightExpandRegular, PanelRightContractRegular } from "@fluentui/react-icons";

import { ActivityPanel } from "./components/ActivityPanel";
import { AssistantReply } from "./components/AssistantReply";
import { Composer } from "./components/Composer";
import { ProgressSteps } from "./components/ProgressSteps";
import { SampleQueries } from "./components/SampleQueries";
import { useChat } from "./hooks/useChat";
import { usePrefersDark } from "./hooks/usePrefersDark";
import type { AssistantMessage } from "./types";

const useStyles = makeStyles({
  provider: { height: "100vh" },
  shell: { display: "flex", height: "100%", backgroundColor: tokens.colorNeutralBackground2 },
  main: { display: "flex", flexDirection: "column", flexGrow: 1, minWidth: 0 },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: `${tokens.spacingVerticalM} ${tokens.spacingHorizontalL}`,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  log: {
    flexGrow: 1,
    overflowY: "auto",
    padding: tokens.spacingHorizontalL,
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
    margin: 0,
    listStyleType: "none",
  },
  bubble: {
    maxWidth: "min(720px, 90%)",
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  user: {
    alignSelf: "flex-end",
    backgroundColor: tokens.colorBrandBackground2,
    whiteSpace: "pre-wrap",
  },
  footer: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
    padding: tokens.spacingHorizontalL,
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
});

export function App() {
  const styles = useStyles();
  const prefersDark = usePrefersDark();
  const chat = useChat();
  const [panelOpen, setPanelOpen] = useState(true);
  const logEnd = useRef<HTMLLIElement>(null);

  const latest = [...chat.messages]
    .reverse()
    .find((m): m is AssistantMessage => m.role === "assistant");

  useEffect(() => {
    logEnd.current?.scrollIntoView?.({ block: "end" });
  }, [chat.messages.length, chat.steps.length, chat.error]);

  return (
    <FluentProvider theme={prefersDark ? webDarkTheme : webLightTheme} className={styles.provider}>
      <div className={styles.shell}>
        <main className={styles.main}>
          <header className={styles.header}>
            <div>
              <Title3 as="h1">NexusCloud Support</Title3>
              <Caption1 as="p">Multi-agent assistant with input and output guardrails</Caption1>
            </div>
            <Button
              appearance="subtle"
              icon={panelOpen ? <PanelRightContractRegular /> : <PanelRightExpandRegular />}
              aria-expanded={panelOpen}
              aria-controls="activity-panel"
              onClick={() => setPanelOpen((open) => !open)}
            >
              {panelOpen ? "Hide agent activity" : "Show agent activity"}
            </Button>
          </header>

          <ol className={styles.log} role="log" aria-live="polite" aria-label="Conversation">
            {chat.messages.length === 0 && (
              <li>
                <Body1>Hi! Ask a question about NexusCloud, or pick a sample below.</Body1>
              </li>
            )}
            {chat.messages.map((message) =>
              message.role === "user" ? (
                <li key={message.id} className={`${styles.bubble} ${styles.user}`} aria-label="You said">
                  <Body1>{message.text}</Body1>
                </li>
              ) : (
                <li key={message.id} className={styles.bubble} aria-label="Assistant replied">
                  <AssistantReply message={message} onRate={chat.rate} />
                </li>
              ),
            )}
            {chat.running && (
              <li className={styles.bubble} role="status">
                <ProgressSteps steps={chat.steps} />
              </li>
            )}
            {chat.error && !chat.running && (
              <li>
                <MessageBar intent="error">
                  <MessageBarBody>
                    <MessageBarTitle>Something went wrong</MessageBarTitle>
                    {chat.error.message}
                  </MessageBarBody>
                  <MessageBarActions>
                    <Button onClick={chat.retry}>Retry</Button>
                  </MessageBarActions>
                </MessageBar>
              </li>
            )}
            {chat.feedbackError && (
              <li>
                <MessageBar intent="warning">
                  <MessageBarBody>{chat.feedbackError}</MessageBarBody>
                </MessageBar>
              </li>
            )}
            <li ref={logEnd} aria-hidden />
          </ol>

          <footer className={styles.footer}>
            <SampleQueries disabled={chat.running} onPick={chat.send} />
            <Composer disabled={chat.running} onSend={chat.send} />
          </footer>
        </main>

        <ActivityPanel open={panelOpen} result={latest?.result ?? null} steps={chat.steps} />
      </div>
    </FluentProvider>
  );
}
