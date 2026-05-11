import { MainLayout } from "@/widgets/layout/MainLayout";
import { StudentClassesSection } from "@/pages/student/ui/StudentClassesSection";

export default function StudentPage() {
  return (
    <MainLayout title="Мои классы" footer="full">
      <StudentClassesSection />
    </MainLayout>
  );
}
