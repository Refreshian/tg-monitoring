import { FormEvent, useState } from "react";
import { createAccessRequest } from "@/lib/api/accessRequests";

type MonitoringRequestFormProps = {
  title?: string;
  initialObject?: string;
  /** Optional preview search query attached to the lead */
  query?: string;
};

export function MonitoringRequestForm({
  title = "Заявка на мониторинг",
  initialObject = "",
  query,
}: MonitoringRequestFormProps) {
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [monitoringObject, setMonitoringObject] = useState(initialObject);
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createAccessRequest({
        contact_name: contactName,
        contact_phone: contactPhone,
        monitoring_object: monitoringObject,
        query: query || undefined,
      });
      setSent(true);
    } catch {
      setError("Не удалось отправить заявку. Попробуйте позже или напишите нам напрямую.");
    } finally {
      setLoading(false);
    }
  }

  if (sent) {
    return (
      <p className="success">
        Заявка отправлена. Мы свяжемся с вами, чтобы подключить мониторинг.
      </p>
    );
  }

  return (
    <form id="monitoring-request" className="access-form" onSubmit={handleSubmit}>
      <h2>{title}</h2>

      <label htmlFor="monitoring-name">Имя</label>
      <input
        id="monitoring-name"
        name="name"
        autoComplete="name"
        value={contactName}
        onChange={(event) => setContactName(event.target.value)}
        required
        minLength={2}
      />

      <label htmlFor="monitoring-phone">Телефон</label>
      <input
        id="monitoring-phone"
        name="phone"
        type="tel"
        autoComplete="tel"
        placeholder="+7 ..."
        value={contactPhone}
        onChange={(event) => setContactPhone(event.target.value)}
        required
        minLength={5}
      />

      <label htmlFor="monitoring-object">Объект мониторинга</label>
      <textarea
        id="monitoring-object"
        name="monitoring_object"
        placeholder="Компания, бренд, персона, событие или поисковые фразы"
        value={monitoringObject}
        onChange={(event) => setMonitoringObject(event.target.value)}
        rows={4}
        required
        minLength={2}
      />

      {error && <p className="error">{error}</p>}

      <button className="button button--primary" type="submit" disabled={loading}>
        {loading ? "Отправляем..." : "Отправить заявку"}
      </button>
    </form>
  );
}
