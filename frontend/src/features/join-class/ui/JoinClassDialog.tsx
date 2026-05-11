import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/shared/ui/dialog";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Plus } from "lucide-react";
import { useJoinClass } from "../model/useJoinClass";

export const JoinClassDialog = ({ fullWidth = false }: { fullWidth?: boolean }) => {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const { joinClass, loading, error, clearError } = useJoinClass();

  const handleJoin = async () => {
    const success = await joinClass(code);
    if (success) {
      setOpen(false);
      setCode("");
    }
  };

  // Сброс ошибки и поля при открытии/закрытии
  useEffect(() => {
    if (!open) {
      setCode("");
      clearError?.();
    }
  }, [open, clearError]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className={fullWidth ? "w-full" : "w-auto"}>
          <Plus className="h-4 w-4 mr-2" />
          Вступить в класс
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Вступить в класс</DialogTitle>
          <DialogDescription>Введите код класса, который вам предоставил учитель.</DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <Label htmlFor="class-code">Код класса</Label>
          <Input
            id="class-code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Например: XYZ123"
            className="mt-2"
          />
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </div>
        <DialogFooter className="flex flex-col sm:flex-row gap-3 sm:gap-0">
          <Button onClick={handleJoin} className="w-full sm:w-auto" disabled={loading}>
            {loading ? "Присоединение..." : "Присоединиться"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
