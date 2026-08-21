const DEMO_ITEMS = [
  {
    source: "Telegram · канал",
    title: "Обзор рынка: что обсуждают сегодня",
    text: "В ленте мониторинга появляются свежие посты и репосты по вашему запросу — с источником, временем и ссылкой на оригинал.",
  },
  {
    source: "Онлайн-СМИ",
    title: "Новость с упоминанием объекта мониторинга",
    text: "Статьи и заметки из онлайн-СМИ собираются в одну ленту вместе с соцмедиа, чтобы ничего не упустить.",
  },
  {
    source: "Соцсеть",
    title: "Публичное обсуждение",
    text: "Комментарии и посты авторов попадают в выдачу с подсветкой ключевых слов — удобно быстро оценить контекст.",
  },
] as const;

export function DemoMentionFeed() {
  return (
    <section className="demo-feed">
      <h2 className="demo-feed__title">Как выглядит лента мониторинга</h2>
      <p className="demo-feed__disclaimer">
        Тексты реальной поисковой выдачи на сайте не публикуются. Ниже — иллюстрация интерфейса:
        так выглядит лента после подключения доступа.
      </p>
      <ul className="demo-feed__list">
        {DEMO_ITEMS.map((item) => (
          <li key={item.title} className="mention-card demo-feed__card">
            <p className="mention-card__source">{item.source}</p>
            <h3>{item.title}</h3>
            <p>{item.text}</p>
            <span className="demo-feed__badge">Пример</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
