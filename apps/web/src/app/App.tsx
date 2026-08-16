import { BrowserRouter, Route, Routes } from "react-router-dom";
import { YandexMetrikaHit } from "@/components/YandexMetrikaHit";
import { SiteLayout } from "@/components/layout/SiteLayout";
import { ContactPage } from "@/pages/ContactPage";
import { HomePage } from "@/pages/HomePage";
import { PreviewPage } from "@/pages/PreviewPage";
import { ServicesPage } from "@/pages/ServicesPage";

export function App() {
  return (
    <BrowserRouter>
      <YandexMetrikaHit />
      <Routes>
        <Route element={<SiteLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/preview" element={<PreviewPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
