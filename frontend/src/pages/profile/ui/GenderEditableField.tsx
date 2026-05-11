import { Gender } from "@/entities/user/model/types";
import { Label } from "@/shared/ui/label";
import { RadioGroup, RadioGroupItem } from "@/shared/ui/radio-group";

interface Props {
  value: Gender | undefined;
  isEditing: boolean;
  onChange: (gender: Gender) => void;
}

export function GenderEditableField({ value, isEditing, onChange }: Props) {
  return (
    <div className="flex flex-col gap-1">
      <Label htmlFor="gender" className="flex items-center gap-2">
        Пол
      </Label>

      {isEditing ? (
        <RadioGroup
          id="gender"
          name="gender"
          defaultValue={value}
          className="flex gap-4 mt-1"
          onValueChange={(val) => onChange(val as Gender)}
        >
          <div className="flex items-center gap-2">
            <RadioGroupItem value="male" id="male" />
            <Label htmlFor="male">Мужской</Label>
          </div>
          <div className="flex items-center gap-2">
            <RadioGroupItem value="female" id="female" />
            <Label htmlFor="female">Женский</Label>
          </div>
        </RadioGroup>
      ) : (
        <p className="mt-1 text-gray-900">{value === "male" ? "Мужской" : "Женский"}</p>
      )}
    </div>
  );
}
