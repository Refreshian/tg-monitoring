import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">Мониторинг репутации</p>
      <h1>Упоминания вашей компании — сразу в Telegram</h1>
      <p className="lead">
        TG-Monitoring подключает аналитику упоминаний из соцсетей, форумов, блогов и СМИ
        и автоматически отправляет найденные сообщения в ваш Telegram.
      </p>
      <div className="actions">
        <Link className="button button--primary" to="/preview">
          Попробовать предпросмотр
        </Link>
        <Link className="button" to="/services">
          Узнать об услуге
        </Link>
      </div>
    </section>
  );
}
