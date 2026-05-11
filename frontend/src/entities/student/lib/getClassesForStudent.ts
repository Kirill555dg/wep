import { classMemberships } from "@/entities/many-to-many/student-classes"
import { mockClasses } from "@/entities/class/model/mock-classes"
import type { ClassInfo } from "@/entities/class/model/types"

/**
 * Возвращает список классов, в которых состоит студент с данным userId
 */
export function getClassesForStudent(userId: number): ClassInfo[] {
  const classIds = classMemberships
    .filter((m) => m.userId === userId)
    .map((m) => m.classId)

  return mockClasses.filter((cls) => classIds.includes(cls.id))
}
