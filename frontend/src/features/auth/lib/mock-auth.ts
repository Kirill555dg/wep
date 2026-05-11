import { mockUsers } from "@/entities/user/model/mock-users"

export const mockCredentials: Record<string, string> = {
  "teacher@school.edu": "123456",
  "student@school.edu": "654321",
}

export function findUserByCredentials(email: string, password: string) {
  const expectedPassword = mockCredentials[email]
  if (!expectedPassword || expectedPassword !== password) return null

  return mockUsers.find((u) => u.email === email) || null
}

export function addMockCredential(email: string, password: string) {
  mockCredentials[email] = password
}

export { mockUsers }