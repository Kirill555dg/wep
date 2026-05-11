import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Textarea } from "@/shared/ui/textarea";

interface Props {
  id: string;
  label: string;
  icon?: React.ReactNode;
  value: string;
  isEditing: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  multiline?: boolean;
  type?: "text" | "email" | "date";
}

function formatTelegramLink(link?: string) {
  if (!link) return "";
  const match = link.match(/(?:t\.me\/|@)([\w\d_]+)/i);
  return match ? `@${match[1]}` : link;
}

function formatVkLink(link?: string) {
  if (!link) return "";
  const match = link.match(/vk\.com\/([\w\d._]+)/i);
  return match ? `vk.com/${match[1]}` : link;
}

export function ProfileEditableField({
  id,
  label,
  icon,
  value,
  isEditing,
  onChange,
  multiline = false,
  type = "text",
}: Props) {
  const isLink = id === "telegram" || id === "vk";
  const isDate = type === "date";

  if (!value && !isEditing) return null;

  return (
    <div className="flex flex-col gap-1">
      <Label htmlFor={id} className="flex items-center gap-2">
        {icon}
        {label}
      </Label>

      {isEditing ? (
        multiline ? (
          <Textarea id={id} name={id} value={value} onChange={onChange} className="mt-1 min-h-[100px]" />
        ) : (
          <Input id={id} name={id} value={value} onChange={onChange} type={isDate ? "date" : type} className="mt-1" />
        )
      ) : isLink && value ? (
        <a
          href={value.startsWith("http") ? value : `https://${value}`}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1 text-blue-600 hover:underline break-words"
        >
          {id === "telegram" ? formatTelegramLink(value) : formatVkLink(value)}
        </a>
      ) : (
        <p className="mt-1 text-gray-900 break-words whitespace-pre-line">{value}</p>
      )}
    </div>
  );
}
