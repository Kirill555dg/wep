import {Navigate, Outlet} from 'react-router-dom';
import {useUserStore} from '@/entities/user/model/store';
import {Loader} from '@/shared/ui/loader';
import {useCurrentUser} from '@/features/auth/api/useAuth';

export default function AuthGuard() {
  const token = useUserStore((s) => s.token);
  const {isLoading} = useCurrentUser();
  const user = useUserStore((s) => s.user);

  if (isLoading && token) return <Loader />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
