import { useEffect, useRef } from "react";

type VolumePriceEstimateProps = {
  weeklyCount?: number | null;
  monthlyEstimate?: number | null;
  priceRub?: number | null;
  priceIsFrom?: boolean;
  tariffName?: string | null;
};

function formatCount(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value);
}

function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value);
}

export function VolumePriceEstimate({
  weeklyCount,
  monthlyEstimate,
  priceRub,
  priceIsFrom = false,
  tariffName,
}: VolumePriceEstimateProps) {
  const ref = useRef<HTMLElement>(null);
  const hasWeekly = weeklyCount != null && weeklyCount >= 0;
  const hasMonthly = monthlyEstimate != null && monthlyEstimate > 0;
  const hasPrice = priceRub != null && priceRub > 0;
  const prefix = priceIsFrom ? "от ~" : "~";

  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [weeklyCount, priceRub]);

  function scrollToForm() {
    document.getElementById("monitoring-request")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <section className="price-estimate" ref={ref} aria-live="polite">
      <h2 className="price-estimate__title">
        Оценка объёма упоминаний и ориентировочная стоимость доступа
      </h2>

      {hasWeekly ? (
        <ul className="price-estimate__stats">
          <li>
            За неделю: <strong>~{formatCount(weeklyCount)} упоминаний</strong>
          </li>
          {hasMonthly ? (
            <li>
              Оценка за месяц: <strong>~{formatCount(monthlyEstimate)} упоминаний</strong>
            </li>
          ) : null}
          {tariffName ? (
            <li>
              Подходящий тариф: <strong>{tariffName}</strong>
            </li>
          ) : null}
        </ul>
      ) : (
        <p className="price-estimate__text">
          Не удалось оценить объём по этому запросу. Оставьте заявку — проверим вручную.
        </p>
      )}

      {hasPrice ? (
        <p className="price-estimate__text">
          Ориентировочная стоимость доступа составит{" "}
          <strong>
            {prefix}
            {formatRub(priceRub)} ₽
          </strong>{" "}
          в месяц.
        </p>
      ) : hasWeekly && weeklyCount > 0 ? (
        <p className="price-estimate__text">
          По запросу есть активность. Оставьте заявку — рассчитаем точную стоимость доступа.
        </p>
      ) : null}

      <button className="button button--primary price-estimate__cta" type="button" onClick={scrollToForm}>
        Перейти к заявке
      </button>
    </section>
  );
}
