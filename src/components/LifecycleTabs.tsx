import { useRef, type KeyboardEvent } from "react";
import type { LifecycleStageId } from "../content/siteContent";

type LifecycleTab = {
  id: LifecycleStageId;
  title: string;
};

type LifecycleTabsProps = {
  idPrefix: string;
  ariaLabel: string;
  tabs: readonly LifecycleTab[];
  selectedId: LifecycleStageId;
  onSelect: (id: LifecycleStageId) => void;
};

export function LifecycleTabs({
  idPrefix,
  ariaLabel,
  tabs,
  selectedId,
  onSelect,
}: LifecycleTabsProps) {
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  function selectIndex(index: number) {
    const tab = tabs[index];
    if (!tab) return;

    onSelect(tab.id);
    tabRefs.current[index]?.focus();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    let nextIndex: number | undefined;

    if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
    if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = tabs.length - 1;
    if (nextIndex === undefined) return;

    event.preventDefault();
    selectIndex(nextIndex);
  }

  return (
    <div className="lifecycle-tab-list" role="tablist" aria-label={ariaLabel}>
      {tabs.map((tab, index) => (
        <button
          key={tab.id}
          ref={(node) => {
            tabRefs.current[index] = node;
          }}
          className="lifecycle-tab"
          type="button"
          role="tab"
          id={`${idPrefix}-tab-${tab.id}`}
          aria-selected={selectedId === tab.id}
          aria-controls={`${idPrefix}-panel-${tab.id}`}
          tabIndex={selectedId === tab.id ? 0 : -1}
          onClick={() => onSelect(tab.id)}
          onKeyDown={(event) => handleKeyDown(event, index)}
        >
          {tab.title}
        </button>
      ))}
    </div>
  );
}
