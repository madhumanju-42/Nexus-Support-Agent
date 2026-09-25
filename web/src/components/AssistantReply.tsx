import {
  Body1,
  Caption1,
  Card,
  CardHeader,
  MessageBar,
  MessageBarBody,
  MessageBarTitle,
  Tag,
  ToggleButton,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import {
  DocumentRegular,
  PersonSupportRegular,
  ThumbDislikeFilled,
  ThumbDislikeRegular,
  ThumbLikeFilled,
  ThumbLikeRegular,
} from "@fluentui/react-icons";
import Markdown from "react-markdown";

import type { AssistantMessage, Rating } from "../types";

// The escalation node appends its summary to the customer message;
// the handoff card shows the summary, so the text shows only the lead-in.
const SUMMARY_MARKER = "**Escalation Summary";

const useStyles = makeStyles({
  root: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalS },
  text: { "& p": { margin: 0, marginBottom: tokens.spacingVerticalXS } },
  sources: { display: "flex", flexWrap: "wrap", gap: tokens.spacingHorizontalXS, alignItems: "center" },
  summary: { whiteSpace: "pre-wrap" },
  feedback: { display: "flex", gap: tokens.spacingHorizontalXS },
});

interface Props {
  message: AssistantMessage;
  onRate: (messageId: string, rating: Rating) => void;
}

export function AssistantReply({ message, onRate }: Props) {
  const styles = useStyles();
  const { result, feedback } = message;
  const text = result.escalated
    ? (result.final_response.split(SUMMARY_MARKER)[0] ?? "").trim()
    : result.final_response;
  const showSources =
    result.agent_used === "knowledge_agent" && !result.escalated && result.sources.length > 0;

  return (
    <div className={styles.root}>
      {result.injection_detected && (
        <MessageBar intent="error">
          <MessageBarBody>
            <MessageBarTitle>Message blocked</MessageBarTitle>
            It looked like an attempt to override the assistant&apos;s instructions, so it
            wasn&apos;t processed.
          </MessageBarBody>
        </MessageBar>
      )}

      {result.pii_detected && !result.injection_detected && (
        <MessageBar intent="info">
          <MessageBarBody>
            <MessageBarTitle>Personal details removed</MessageBarTitle>
            We redacted your {result.pii_redacted_fields.join(", ").replace(/_/g, " ")} before
            processing.
          </MessageBarBody>
        </MessageBar>
      )}

      <div className={styles.text}>
        <Markdown>{text}</Markdown>
      </div>

      {result.escalated && (
        <Card appearance="outline" aria-label="Human handoff">
          <CardHeader
            image={<PersonSupportRegular fontSize={24} aria-hidden />}
            header={<Body1><b>Handed off to a support specialist</b></Body1>}
            description={<Caption1>Summary shared with the support team</Caption1>}
          />
          <Body1 className={styles.summary}>
            {result.context_summary ?? "No summary available."}
          </Body1>
        </Card>
      )}

      {showSources && (
        <div className={styles.sources} role="group" aria-label="Sources retrieved from the knowledge base">
          <Caption1>Sources:</Caption1>
          {result.sources.map((source) => (
            <Tag key={source} size="small" appearance="outline" icon={<DocumentRegular />}>
              {source}
            </Tag>
          ))}
        </div>
      )}

      <div className={styles.feedback} role="group" aria-label="Rate this reply">
        <ToggleButton
          size="small"
          appearance="subtle"
          checked={feedback === "up"}
          icon={feedback === "up" ? <ThumbLikeFilled /> : <ThumbLikeRegular />}
          aria-label="Helpful"
          onClick={() => onRate(message.id, "up")}
        />
        <ToggleButton
          size="small"
          appearance="subtle"
          checked={feedback === "down"}
          icon={feedback === "down" ? <ThumbDislikeFilled /> : <ThumbDislikeRegular />}
          aria-label="Not helpful"
          onClick={() => onRate(message.id, "down")}
        />
      </div>
    </div>
  );
}
