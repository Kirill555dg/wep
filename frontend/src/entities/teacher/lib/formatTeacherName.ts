import type { Teacher } from "../model/types"

export function formatTeacherName(teacher: Teacher): string {
  return `${teacher.lastName} ${teacher.firstName} ${teacher.middleName ?? ""}`
}
