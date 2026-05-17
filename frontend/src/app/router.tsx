import {Routes, Route, Navigate} from 'react-router-dom';
import CatalogPage from '@/pages/catalog/CatalogPage';
import EditorPage from '@/pages/editor/EditorPage';
import TakeTestPage from '@/pages/take-test/TakeTestPage';
import ResultsPage from '@/pages/results/ResultsPage';
import LoginPage from '@/pages/login/LoginPage';
import RegisterPage from '@/pages/register/RegisterPage';
import ProfilePage from '@/pages/profile/ProfilePage';
import StatsPage from '@/pages/stats/StatsPage';
import AuthGuard from './guards/AuthGuard';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<AuthGuard />}>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/editor/:testId?" element={<EditorPage />} />
        <Route path="/take/:testId" element={<TakeTestPage />} />
        <Route path="/results/:attemptId" element={<ResultsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/stats" element={<StatsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
