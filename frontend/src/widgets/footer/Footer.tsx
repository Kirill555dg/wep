import { SocialIcon } from "@/shared/ui/social-icon";
import { Mail, MapPin, Phone } from "lucide-react";

interface FooterProps {
  mode?: "full" | "compact";
}

export function Footer({ mode = "compact" }: FooterProps) {
  return (
    <footer className="bg-blue-900 text-white">
      {mode === "full" && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">О платформе</h3>
              <p className="text-blue-200">
                WEP — современная образовательная платформа для эффективного взаимодействия учителей и учеников.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Контакты</h3>
              <ul className="space-y-2 text-blue-200">
                <li className="flex items-center">
                  <Mail className="h-4 w-4 mr-2" />
                  <span>support@wep-edu.ru</span>
                </li>
                <li className="flex items-center">
                  <Phone className="h-4 w-4 mr-2" />
                  <span>+7 (999) 123-45-67</span>
                </li>
                <li className="flex items-center">
                  <MapPin className="h-4 w-4 mr-2" />
                  <span>г. Москва, ул. Образовательная, 42</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Разработчик</h3>

              <div className="flex flex-col gap-2 text-blue-200">
                <p>Миркин Кирилл Леонидович</p>

                <a
                  href="https://github.com/Kirill555dg"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-white hover:text-blue-200 transition-colors"
                >
                  <SocialIcon type="github" className="text-inherit h-5 w-5" />
                  <span className="text-sm">GitHub: Kirill555dg</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="border-t border-blue-800 text-center text-blue-200 text-sm py-4">
        © 2025 WEP. Все права защищены.
      </div>
    </footer>
  );
}
