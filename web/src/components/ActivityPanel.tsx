import type { ReactNode } from "react";
import {
  Badge,
  Body1,
  Caption1,
  DrawerBody,
  DrawerHeader,
  DrawerHeaderTitle,
  InlineDrawer,
  makeStyles,
  tokens,
} from "@fluentui/react-components";

import type { ChatResult, NodeEvent } from "../types";

const useStyles = makeStyles({
  list: {
    display: "grid",
    gridTemplateColumns: "auto 1fr",
    columnGap: tokens.spacingHorizontalM,
    rowGap: tokens.spacingVerticalXS,
    margin: 0,
  },
  term: { color: tokens.colorNeutralForeground2 },
  value: { margin: 0, overflowWrap: "anywhere" },
  section: { marginTop: tokens.spacingVerticalL },
  code: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
    backgroundColor: tokens.colorNeutralBackground3,
    padding: tokens.spacingHorizontalXS,
    borderRadius: tokens.borderRadiusSmall,
    whiteSpace: "pre-wrap",
    margin: 0,
  },
  badges: { display: "flex", flexWrap: "wrap", gap: tokens.spacingHorizontalXS },
});

interface Props {
  open: boolean;
  result: ChatResult | null;
  steps: NodeEvent[];
}

function Row({ term, children }: { term: string; children: ReactNode }) {
  const styles = useStyles();
  return (
    <>
      <dt className={styles.term}>{term}</dt>
      <dd className={styles.value}>{children}</dd>
    </>
  );
}

export function ActivityPanel({ open, result, steps }: Props) {
  const styles = useStyles();
  const flags = result
    ? [
        ...(result.injection_detected ? ["injection blocked"] : []),
        ...result.pii_redacted_fields.map((f) => `pii: ${f}`),
        ...result.output_flags.filter((f) => f !== "injection_blocked"),
      ]
    : [];

  return (
    <InlineDrawer id="activity-panel" open={open} position="end" separator>
      <DrawerHeader>
        <DrawerHeaderTitle heading={{ as: "h2" }}>Agent activity</DrawerHeaderTitle>
      </DrawerHeader>
      <DrawerBody>
        {!result ? (
          <Body1>Send a message to see how the agents handled it.</Body1>
        ) : (
          <>
            <Caption1>Latest reply</Caption1>
            <dl className={styles.list}>
              <Row term="Intent">{result.intent ?? "—"}</Row>
              <Row term="Urgency">{result.urgency ?? "—"}</Row>
              <Row term="Agent">{result.agent_used ?? "—"}</Row>
              <Row term="Confidence">
                {result.confidence === null ? "—" : `${Math.round(result.confidence * 100)}% (self-reported)`}
              </Row>
              <Row term="Escalated">{result.escalated ? "Yes" : "No"}</Row>
            </dl>

            <section className={styles.section} aria-label="Pipeline steps">
              <Caption1>Steps</Caption1>
              <Body1 as="p">{steps.map((s) => s.label).join(" → ") || "—"}</Body1>
            </section>

            <section className={styles.section} aria-label="Tools called">
              <Caption1>Tools called</Caption1>
              {result.tool_calls.length === 0 ? (
                <Body1 as="p">None</Body1>
              ) : (
                result.tool_calls.map((call, i) => (
                  <div key={`${call.tool}-${i}`}>
                    <Body1 as="p"><b>{call.tool}</b></Body1>
                    <pre className={styles.code}>{JSON.stringify(call.args, null, 2)}</pre>
                  </div>
                ))
              )}
            </section>

            <section className={styles.section} aria-label="Guardrail flags">
              <Caption1>Guardrail flags</Caption1>
              <div className={styles.badges}>
                {flags.length === 0 ? (
                  <Body1>None</Body1>
                ) : (
                  flags.map((flag) => (
                    <Badge key={flag} appearance="tint" color="warning">
                      {flag}
                    </Badge>
                  ))
                )}
              </div>
            </section>
          </>
        )}
      </DrawerBody>
    </InlineDrawer>
  );
}
