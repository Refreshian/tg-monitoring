type PriceEstimateProps = {
  priceRub: number;
  priceIsFrom?: boolean;
};

function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value);
}

export function PriceEstimate({ priceRub, priceIsFrom = false }: PriceEstimateProps) {
  const prefix = priceIsFrom ? "от ~" : "~";

  return (
    <section className="price-estimate" aria-live="polite">
      <p className="price-estimate__text">
        Стоимость доступа по запросу составит{" "}
        <strong>
          {prefix}
          {formatRub(priceRub)} ₽
        </strong>
        . Оставьте заявку — подключим мониторинг под ваш объём.
      </p>
    </section>
  );
}
