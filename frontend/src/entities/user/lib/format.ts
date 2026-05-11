export function getFullNameAdaptive(
  user: { lastName?: string; firstName?: string; middleName?: string },
  showMiddle: boolean
) {
  const parts = [user.lastName, user.firstName]
  if (showMiddle && user.middleName) {
    parts.push(user.middleName)
  }
  return parts.filter(Boolean).join(" ")
}
