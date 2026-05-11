import { useEffect } from "react";
import { useUserStore } from "@/entities/user/model/store";
import { useClassStore } from "@/entities/class/model/store";
import { getClassesForStudent } from "@/entities/student/lib/getClassesForStudent";

export const ClassBootstrapper = () => {
  const user = useUserStore((s) => s.user);
  const resetClasses = useClassStore((s) => s.resetClasses);

  useEffect(() => {
    if (user && user.role === "student") {
      const classes = getClassesForStudent(user.id);
      resetClasses(classes);
    }
  }, [user, resetClasses]);

  return null;
};
