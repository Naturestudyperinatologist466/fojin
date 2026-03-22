import { useTranslation } from "react-i18next";
import { Checkbox, Button } from "antd";
import { useTimelineStore } from "../../stores/timelineStore";

const CATEGORY_OPTIONS = [
  { label: "经 Sūtra", value: "sutra" },
  { label: "律 Vinaya", value: "vinaya" },
  { label: "论 Abhidharma", value: "abhidharma" },
  { label: "疏 Commentary", value: "commentary" },
];

export default function TimelineFilters() {
  const { t } = useTranslation();
  const { filters, setFilter, resetFilters } = useTimelineStore();

  return (
    <div className="timeline-filters">
      <h4>{t("timeline.filterCategory", "分类")}</h4>
      <Checkbox.Group
        options={CATEGORY_OPTIONS}
        value={filters.category ? [filters.category] : []}
        onChange={(vals) => {
          const last = vals.length > 0 ? String(vals[vals.length - 1]) : null;
          setFilter("category", last);
        }}
        style={{ display: "flex", flexDirection: "column", gap: 6 }}
      />

      <div style={{ marginTop: 16 }}>
        <Button size="small" onClick={resetFilters}>
          {t("common.reset", "重置")}
        </Button>
      </div>
    </div>
  );
}
