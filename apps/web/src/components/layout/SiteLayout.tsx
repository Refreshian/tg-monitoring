import { NavLink, Outlet } from "react-router-dom";

export function SiteLayout() {
  return (
    <div className="layout">
      <header className="site-header">
        <div className="container site-header__inner">
          <NavLink to="/" className="brand">
            TG-Monitoring
          </NavLink>
          <nav className="nav" aria-label="Основная навигация">
            <NavLink to="/" end>
              Главная
            </NavLink>
            <NavLink to="/services">Услуги</NavLink>
            <NavLink to="/preview">Предпросмотр</NavLink>
            <NavLink to="/contact">Контакты</NavLink>
          </nav>
        </div>
      </header>

      <main className="site-main">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="container site-footer__inner">
          <span className="brand brand--footer">TG-Monitoring</span>
          <p>Мониторинг социальных медиа и онлайн-СМИ</p>
          <p className="site-footer__copy">© {new Date().getFullYear()} TG-Monitoring</p>
        </div>
      </footer>
    </div>
  );
}
