import { FormEvent, useState } from "react";
import { createAccessRequest } from "@/lib/api/accessRequests";

type AccessRequestFormProps = {
  query: string;
};

export function AccessRequestForm({ query }: AccessRequestFormProps) {
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    try {
      await createAccessRequest({
        query,
        contact_name: contactName,
        contact_email: contactEmail,
        contact_phone: contactPhone || undefined,
        message: message || undefined,
      });
      setSent(true);
    } finally {
      setLoading(false);
    }
  }

  if (sent) {
    return <p className="success">Заявка отправлена. Мы свяжемся с вами для подключения.</p>;
  }

  return (
    <form className="access-form" onSubmit={handleSubmit}>
      <h2>Заказать доступ</h2>
      <label htmlFor="contactName">Имя</label>
      <input
        id="contactName"
        value={contactName}
        onChange={(event) => setContactName(event.target.value)}
        required
      />
      <label htmlFor="contactEmail">Email</label>
      <input
        id="contactEmail"
        type="email"
        value={contactEmail}
        onChange={(event) => setContactEmail(event.target.value)}
        required
      />
      <label htmlFor="contactPhone">Телефон</label>
      <input
        id="contactPhone"
        value={contactPhone}
        onChange={(event) => setContactPhone(event.target.value)}
      />
      <label htmlFor="message">Комментарий</label>
      <textarea
        id="message"
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        rows={3}
      />
      <button className="button button--primary" type="submit" disabled={loading}>
        {loading ? "Отправляем..." : "Отправить заявку"}
      </button>
    </form>
  );
}
