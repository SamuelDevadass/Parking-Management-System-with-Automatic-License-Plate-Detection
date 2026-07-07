import { Fragment } from "react";

/*
  StepBar mirrors the page-flow of the original Tkinter app (each Frame was
  a step the attendant moved through). The numbering is meaningful here —
  it's a real sequence, not decoration — so numbered markers earn their
  place.
*/
const STEPS = [
  { key: "wing", label: "Wing" },
  { key: "spots", label: "Spots" },
  { key: "detect", label: "Detect" },
  { key: "owner", label: "Owner" },
  { key: "entry-exit", label: "Entry / Exit" },
  { key: "billing", label: "Billing" },
];

export default function StepBar({ current }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current);

  return (
    <nav className="step-bar" aria-label="Progress">
      {STEPS.map((step, i) => {
        const state =
          i === currentIndex ? "active" : i < currentIndex ? "done" : "upcoming";
        return (
          <Fragment key={step.key}>
            <div className={`step-bar__item step-bar__item--${state}`}>
              <div className="step-bar__marker">{i < currentIndex ? "✓" : i + 1}</div>
              <div className="step-bar__label">{step.label}</div>
            </div>
            {i < STEPS.length - 1 && <div className="step-bar__line" />}
          </Fragment>
        );
      })}
    </nav>
  );
}
