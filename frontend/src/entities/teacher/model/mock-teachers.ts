import { mockUsers } from "@/entities/user/model/mock-users"
import { Teacher } from "./types"

const teacherUser = mockUsers.find((u) => u.id === 1)!

export const mockTeachers: Teacher[] = [
  {
    id: teacherUser.id,
    firstName: teacherUser.firstName,
    lastName: teacherUser.lastName,
    middleName: teacherUser.middleName,
    email: teacherUser.email,
    gender: teacherUser.gender,
    avatar: teacherUser.avatar,
  },
]