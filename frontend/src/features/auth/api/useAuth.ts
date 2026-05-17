import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {toast} from '@/shared/hooks/use-toast';
import {useUserStore} from '@/entities/user/model/store';
import {
  loginApiV1AuthLoginPost,
  registerApiV1AuthRegisterPost,
  getCurrentUserProfileApiV1AuthMeGet,
} from '@/shared/api/client/auth';
import {LoginRequest, UserCreate} from '@/shared/api/client/testConstructorAPI.schemas';

export function useLogin() {
  const setToken = useUserStore((s) => s.setToken);
  const setUser = useUserStore((s) => s.setUser);
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: LoginRequest) => loginApiV1AuthLoginPost(data),
    onSuccess: (res) => {
      if ('data' in res && res.data.access_token) {
        setToken(res.data.access_token);
        setUser(res.data.user);
        qc.invalidateQueries({queryKey: ['auth', 'me']});
      }
      toast({title: 'Вход выполнен'});
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'});
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: UserCreate) => registerApiV1AuthRegisterPost(data),
    onSuccess: () => {
      toast({title: 'Регистрация выполнена'});
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'});
    },
  });
}

export function useCurrentUser() {
  const token = useUserStore((s) => s.token);
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => getCurrentUserProfileApiV1AuthMeGet(),
    retry: false,
    enabled: !!token,
  });
}
