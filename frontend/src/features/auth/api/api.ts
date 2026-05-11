import type { User } from "@/entities/user/model/types"
import type { LoginData, RegisterData } from "@/features/auth/model/schema"

export interface AuthApi {
  login(data: LoginData): Promise<User>
  register(data: RegisterData): Promise<User>
  resetPassword(email: string): Promise<void>
  checkAuth(): Promise<User | null>
}

export let authApi: AuthApi

export function setAuthApi(impl: AuthApi) {
  authApi = impl
}
