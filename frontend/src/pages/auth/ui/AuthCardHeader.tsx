import { CardHeader, CardTitle, CardDescription } from "@/shared/ui/card";

type Props = {
  title: string;
  description: string;
  center?: boolean;
};

export function AuthCardHeader({ title, description, center = true }: Props) {
  return (
    <CardHeader>
      <CardTitle className={center ? "text-2xl text-center" : "text-2xl"}>{title}</CardTitle>
      <CardDescription className={center ? "text-center" : ""}>{description}</CardDescription>
    </CardHeader>
  );
}
