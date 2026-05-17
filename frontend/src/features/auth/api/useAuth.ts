import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
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
  return useMutation({
    mutationFn: (data: LoginRequest) => loginApiV1AuthLoginPost(data),
    onSuccess: (res) => {
      if ('data' in res && res.data.access_token) {
        setToken(res.data.access_token);
        setUser(res.data.user);
      }
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: UserCreate) => registerApiV1AuthRegisterPost(data),
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => getCurrentUserProfileApiV1AuthMeGet(),
    retry: false,
  });
}
