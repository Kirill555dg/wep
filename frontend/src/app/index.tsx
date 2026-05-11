import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "@/pages/auth/login/LoginPage";
import RegisterPage from "@/pages/auth/register/RegisterPage";
import ResetPasswordPage from "@/pages/auth/reset-password/ResetPasswordPage";
import ProfilePage from "@/pages/profile/ProfilePage";
import StudentPage from "@/pages/student/StudentPage";
import TeacherPage from "@/pages/teacher/TeacherPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import { Toaster } from "@/shared/ui/toaster";
import AuthBootstrapper from "./providers/AuthBootstrapper";
import RoleProtectedRoute from "./router/RoleProtectedRoute";
import AuthProtectedRoute from "./router/AuthProtectedRoute ";
import { MainRedirect } from "./router/MainRedirect";
import { ClassBootstrapper } from "./providers/ClassBootstrapper";

function App() {
  return (
    <>
      <Toaster />
      <AuthBootstrapper />
      <ClassBootstrapper />

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route element={<AuthProtectedRoute />}>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/notifications" element={<NotificationsPage />} />

          <Route element={<RoleProtectedRoute requiredRole="student" />}>
            <Route path="/student" element={<StudentPage />} />
          </Route>

          <Route element={<RoleProtectedRoute requiredRole="teacher" />}>
            <Route path="/teacher" element={<TeacherPage />} />
          </Route>

          <Route path="/" element={<MainRedirect />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;
