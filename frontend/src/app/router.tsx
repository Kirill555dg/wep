import {Routes, Route, Navigate} from 'react-router-dom'
import CatalogPage from '@/pages/catalog/CatalogPage'
import TestViewPage from '@/pages/test-view/TestViewPage'
import TakeTestPage from '@/pages/test-content/TakeTestPage'
import TypstEditorPage from '@/pages/test-content/TypstEditorPage'
import HistoryPage from '@/pages/history/HistoryPage'
import MyTestsPage from '@/pages/my-tests/MyTestsPage'
import ResultsPage from '@/pages/results/ResultsPage'
import LoginPage from '@/pages/login/LoginPage'
import RegisterPage from '@/pages/register/RegisterPage'
import ProfilePage from '@/pages/profile/ProfilePage'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/catalog" replace />} />
      <Route path="/catalog" element={<CatalogPage />} />
      <Route path="/tests/:testId" element={<TestViewPage />} />
      <Route path="/tests/:testId/take" element={<TakeTestPage />} />
      <Route path="/tests/:testId/edit" element={<TakeTestPage editMode />} />
      <Route path="/tests/:testId/questions/:questionId/typst" element={<TypstEditorPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/my-tests" element={<MyTestsPage />} />
      <Route path="/attempts/:attemptId" element={<ResultsPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="*" element={<Navigate to="/catalog" replace />} />
    </Routes>
  )
}
