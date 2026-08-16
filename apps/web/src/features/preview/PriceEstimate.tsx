import { useEffect, useRef } from "react";

type PriceEstimateProps = {
  priceRub?: number | null;
  priceIsFrom?: boolean;
};

function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value);
}

export function PriceEstimate({ priceRub, priceIsFrom = false }: PriceEstimateProps) {
  const ref = useRef<HTMLElement>(null);
  const hasPrice = priceRub != null && priceRub > 0;
  const prefix = priceIsFrom ? "от ~" : "~";

  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [priceRub]);

  function scrollToForm() {
    document.getElementById("monitoring-request")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <section className="price-estimate" ref={ref} aria-live="polite">
      <h2 className="price-estimate__title">Ориентировочная стоимость</h2>
      {hasPrice ? (
        <p className="price-estimate__text">
          Стоимость доступа по запросу составит{" "}
          <strong>
            {prefix}
            {formatRub(priceRub)} ₽
          </strong>{" "}
          в месяц.
        </p>
      ) : (
        <p className="price-estimate__text">
          По этому запросу уже есть упоминания. Оставьте заявку — рассчитаем точную стоимость
          доступа под ваш объём.
        </p>
      )}
      <button className="button button--primary price-estimate__cta" type="button" onClick={scrollToForm}>
        Перейти к заявке
      </button>
    </section>
  );
}
