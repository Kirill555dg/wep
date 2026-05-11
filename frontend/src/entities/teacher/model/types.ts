import type { User } from "@/entities/user/model/types"

export type Teacher = Pick<
  User,
  "id" | "firstName" | "lastName" | "middleName" | "email" | "avatar" | "gender"
>
