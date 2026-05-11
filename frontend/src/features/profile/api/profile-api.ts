import type { User } from "@/entities/user/model/types"

export interface ProfileApi {
  updateProfile(data: Partial<User>): Promise<User>
}

export let profileApi: ProfileApi

export function setProfileApi(impl: ProfileApi) {
  profileApi = impl
}
