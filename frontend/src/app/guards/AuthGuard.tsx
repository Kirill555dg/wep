import {Navigate, Outlet} from 'react-router-dom';
import {useUserStore} from '@/entities/user/model/store';

export default function AuthGuard() {
  const token = useUserStore((s) => s.token);

  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
}
