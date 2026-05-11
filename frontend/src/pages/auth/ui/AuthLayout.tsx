import { ReactNode } from "react";
import { GraduationCap } from "lucide-react";

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col justify-between bg-gray-50 p-4">
      <div className="flex flex-col items-center justify-center flex-1">
        <div className="w-full max-w-md">
          <div className="flex justify-center mb-8">
            <div className="flex items-center">
              <div className="bg-blue-900 rounded-full p-3 mr-3 flex items-center justify-center">
                <GraduationCap className="text-white h-8 w-8" />
              </div>
              <h1 className="text-4xl font-bold text-blue-900">WEP</h1>
            </div>
          </div>
          {children}
        </div>
      </div>
      <footer className="text-center text-sm text-muted-foreground py-4">
        <p>© 2025 WEP. Все права защищены.</p>
      </footer>
    </div>
  );
}
