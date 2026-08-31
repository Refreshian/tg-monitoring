import { FormEvent, useState } from "react";
import { sendPreviewSamples } from "@/lib/api/preview";

type PreviewSamplesEmailFormProps = {
  sampleToken: string;
};

export function PreviewSamplesEmailForm({ sampleToken }: PreviewSamplesEmailFormProps) {
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await sendPreviewSamples(sampleToken, email.trim());
      setMessage(result.message);
    } catch {
      setError("Не удалось отправить примеры. Попробуйте позже.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="samples-email-form">
      <h2 className="samples-email-form__title">Получить 10 примеров на email</h2>
      <p className="samples-email-form__lead">
        Отправим до десяти примеров упоминаний по вашему запросу (преимущественно из VK, если
        есть в выдаче) и ссылку для просмотра на сайте.
      </p>
      <form className="samples-email-form__form" onSubmit={handleSubmit}>
        <label htmlFor="samples-email">Email</label>
        <input
          id="samples-email"
          name="email"
          type="email"
          autoComplete="email"
          placeholder="you@company.ru"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <label className="samples-email-form__consent">
          <input
            type="checkbox"
            checked={consent}
            onChange={(event) => setConsent(event.target.checked)}
            required
          />
          <span>Согласен на обработку данных для отправки примеров</span>
        </label>
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}
        <button className="button button--primary" type="submit" disabled={loading}>
          {loading ? "Отправляем..." : "Получить примеры на email"}
        </button>
      </form>
    </section>
  );
}
