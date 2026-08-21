import { Link } from "react-router-dom";

export function ServicesPage() {
  return (
    <section className="page">
      <div className="container page__inner">
        <h1>Услуги</h1>
        <p className="page__lead">
          Полный цикл работы с информационным полем: от сбора упоминаний до аналитики
          и отчётов.
        </p>

        <div className="service-grid">
          <article className="service-block">
            <h2>Мониторинг соцмедиа и СМИ</h2>
            <p>
              Оперативный настроенный мониторинг упоминаний компании, персоны, бренда или
              события во всех ключевых социальных медиа и онлайн-СМИ.
            </p>
          </article>
          <article className="service-block">
            <h2>Аналитика и отчёты</h2>
            <p>
              Анализ соцмедиа и СМИ: инфоповоды, тональность, динамика упоминаний и готовые
              отчёты для принятия решений.
            </p>
          </article>
          <article className="service-block">
            <h2>Доставка в Telegram</h2>
            <p>
              Собранные упоминания автоматически направляются в ваш Telegram — быстро и без
              лишних интерфейсов.
            </p>
          </article>
          <article className="service-block">
            <h2>Оценка объёма перед заказом</h2>
            <p>
              До подключения услуги можно оценить объём упоминаний по вашему запросу и
              ориентировочную стоимость доступа прямо на сайте.
            </p>
          </article>
        </div>

        <div className="page__cta">
          <Link className="button button--primary" to="/preview">
            Оценить объём и стоимость
          </Link>
        </div>
      </div>
    </section>
  );
}
