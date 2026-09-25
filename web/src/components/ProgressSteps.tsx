import { Caption1, Spinner, makeStyles, tokens } from "@fluentui/react-components";
import { CheckmarkCircle16Regular } from "@fluentui/react-icons";

import type { NodeEvent } from "../types";

const useStyles = makeStyles({
  root: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingVerticalS,
  },
  list: { margin: 0, padding: 0, listStyleType: "none" },
  step: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalXS,
    color: tokens.colorNeutralForeground2,
  },
  done: { color: tokens.colorPaletteGreenForeground1 },
});

interface Props {
  steps: NodeEvent[];
}

/** Live pipeline progress while the agent graph runs. */
export function ProgressSteps({ steps }: Props) {
  const styles = useStyles();
  const current = steps.at(-1)?.label ?? "Starting";

  return (
    <div className={styles.root} data-testid="progress">
      {steps.length > 0 && (
        <ol className={styles.list} aria-label="Completed steps">
          {steps.map((step) => (
            <li key={step.index} className={styles.step}>
              <CheckmarkCircle16Regular className={styles.done} aria-hidden />
              <Caption1>{step.label}</Caption1>
            </li>
          ))}
        </ol>
      )}
      <Spinner size="tiny" label={`Working… last step: ${current}`} labelPosition="after" />
    </div>
  );
}
