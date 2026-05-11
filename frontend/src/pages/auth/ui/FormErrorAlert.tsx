type Props = { message: string | null };

export function FormErrorAlert({ message }: Props) {
  if (!message) return null;

  return <div className="p-3 bg-red-50 text-red-600 text-sm rounded-md">{message}</div>;
}
