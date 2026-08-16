import { Link } from "react-router-dom";
import { MonitoringRequestForm } from "@/features/access-request/MonitoringRequestForm";

export function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero__media" aria-hidden="true">
          <img src="/hero-dashboard.png" alt="" className="hero__image" />
          <div className="hero__veil" />
        </div>

        <div className="container hero__content">
          <p className="hero__brand animate-rise">TG-Monitoring</p>
          <h1 className="hero__title animate-rise animate-rise--delay-1">
            Лучший мониторинг по цене и скорости
          </h1>
          <p className="hero__lead animate-rise animate-rise--delay-2">
            Оперативный сбор упоминаний из соцсетей и онлайн-СМИ с доставкой результатов
            в Telegram.
          </p>
          <div className="hero__actions animate-rise animate-rise--delay-3">
            <Link className="button button--primary" to="/preview">
              Попробовать предпросмотр
            </Link>
            <Link className="button button--ghost" to="/contact">
              Оставить заявку
            </Link>
          </div>
        </div>
      </section>

      <section className="section about">
        <div className="container section__narrow">
          <h2>Надёжный мониторинг для бизнеса и агентств</h2>
          <p>
            Работаем на рынке более 12 лет. Предоставляем оперативный настроенный мониторинг
            социальных медиа и онлайн-СМИ, занимаемся анализом соцмедиа и СМИ — аналитика,
            отчёты, разбор инфоповодов.
          </p>
          <p>
            Гарантируем лучший сбор с источников и лучшие цены для заказчиков. Среди наших
            клиентов — и прямые заказчики (компании), и агентства.
          </p>
          <Link className="text-link" to="/services">
            Подробнее об услугах →
          </Link>
        </div>
      </section>

      <section className="section section--accent">
        <div className="container section__narrow">
          <h2>Проверьте сбор до подключения</h2>
          <p>
            Введите поисковый запрос и посмотрите последние найденные упоминания — без
            обязательств и до заказа доступа.
          </p>
          <Link className="button button--primary" to="/preview">
            Открыть предпросмотр
          </Link>
        </div>
      </section>

      <section className="section" id="request">
        <div className="container page__inner--narrow">
          <MonitoringRequestForm title="Оставить заявку на мониторинг" />
        </div>
      </section>
    </>
  );
}
