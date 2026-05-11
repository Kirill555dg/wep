import { mockTeachers } from "../model/mock-teachers"
import type { Teacher } from "../model/types"

export function getTeacherById(id: number): Teacher | undefined {
  return mockTeachers.find((t) => t.id === id)
}
