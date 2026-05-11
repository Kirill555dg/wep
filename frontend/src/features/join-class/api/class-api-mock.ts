import { mockClasses } from "@/entities/class/model/mock-classes"
import type { ClassInfo } from "@/entities/class/model/types"

export async function getClassByCode(code: string): Promise<ClassInfo | null> {
  await new Promise((r) => setTimeout(r, 300)) // имитация запроса
  return mockClasses.find((cls) => cls.entryCode.toLowerCase() === code.toLowerCase()) || null
}
