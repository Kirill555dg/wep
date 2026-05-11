import { classMemberships } from "@/entities/many-to-many/student-classes"
import { mockStudents } from "@/entities/student/model/mock-students"
import type { Student } from "@/entities/student/model/types"

/**
 * Возвращает список студентов, состоящих в заданном классе
 */
export function getStudentsInClass(classId: number): Student[] {
  const userIds = classMemberships
    .filter((m) => m.classId === classId)
    .map((m) => m.userId)

  return mockStudents.filter((student) => userIds.includes(student.id))
}
