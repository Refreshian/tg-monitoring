export function ContactPage() {
  return (
    <section className="page">
      <div className="container page__inner page__inner--narrow">
        <h1>Контакты</h1>
        <p className="page__lead">
          Напишите нам, чтобы подключить мониторинг или обсудить задачу для вашей компании
          или агентства.
        </p>

        <ul className="contact-list">
          <li>
            <span className="contact-list__label">E-mail</span>
            <a href="mailto:monitoringsystem@bk.ru">monitoringsystem@bk.ru</a>
          </li>
          <li>
            <span className="contact-list__label">Telegram</span>
            <a href="https://t.me/alexpetrov7" target="_blank" rel="noreferrer">
              @alexpetrov7
            </a>
          </li>
        </ul>
      </div>
    </section>
  );
}
