import { NavLink, Outlet } from "react-router-dom";

export function SiteLayout() {
  return (
    <div className="layout">
      <header className="header">
        <div className="container header__inner">
          <NavLink to="/" className="logo">
            TG-Monitoring
          </NavLink>
          <nav className="nav">
            <NavLink to="/">Главная</NavLink>
            <NavLink to="/services">Услуги</NavLink>
            <NavLink to="/preview">Предпросмотр</NavLink>
            <NavLink to="/contact">Контакты</NavLink>
          </nav>
        </div>
      </header>
      <main className="main container">
        <Outlet />
      </main>
      <footer className="footer">
        <div className="container">© {new Date().getFullYear()} TG-Monitoring</div>
      </footer>
    </div>
  );
}
