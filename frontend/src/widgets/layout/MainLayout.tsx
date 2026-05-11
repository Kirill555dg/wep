import { ResponsiveHeader } from "@/widgets/header/ResponsiveHeader";
import { Footer } from "@/widgets/footer/Footer";

interface MainLayoutProps {
  title?: string;
  back?: { label: string; to: string };
  footer?: "full" | "compact";
  children: React.ReactNode;
}

export function MainLayout({ title, back, footer = "compact", children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-white sm:bg-gray-100 flex flex-col">
      <ResponsiveHeader title={title} overrideBack={back} />
      <main className="flex-1 w-full sm:max-w-7xl mx-auto px-0 sm:px-6 lg:px-8 py-4 sm:py-8">{children}</main>
      <Footer mode={footer} />
    </div>
  );
}
