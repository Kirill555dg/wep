import { User } from "@/entities/user/model/types"

export interface Student extends Pick<User,
  "id" | "firstName" | "lastName" | "email" | "avatar" | "gender"
> {
  averageGrade: number
  lastActive: string
}
