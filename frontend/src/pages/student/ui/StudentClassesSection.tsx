import { useClassStore } from "@/entities/class/model/store";
import { ClassCard } from "@/entities/class/ui/ClassCard";
import { formatTeacherName } from "@/entities/teacher/lib/formatTeacherName";
import { getTeacherById } from "@/entities/teacher/lib/getTeacherById";
import { JoinClassDialog } from "@/features/join-class/ui/JoinClassDialog";
import { useMediaQuery } from "@/shared/hooks/use-media-query";

export const StudentClassesSection = () => {
  const classes = useClassStore((s) => s.joinedClasses);
  const isNarrow = useMediaQuery("(max-width: 440px)");

  return (
    <section className="w-full sm:max-w-7xl mx-auto px-4 sm:px-0 py-4 sm:py-0">
      <header className="flex flex-wrap justify-between items-start sm:items-center mb-6 gap-4">
        <h2 className="text-xl font-semibold text-gray-800">Текущие классы</h2>
        <div className={isNarrow ? "w-full" : "w-auto"}>
          <JoinClassDialog fullWidth={isNarrow} />
        </div>
      </header>

      {classes.length === 0 ? (
        <p className="text-gray-600 text-sm">Вы ещё не присоединились ни к одному классу.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes.map((cls) => {
            const teacher = getTeacherById(cls.teacherId);
            const teacherName = teacher ? formatTeacherName(teacher) : "Неизвестный преподаватель";

            return (
              <ClassCard
                key={cls.id}
                id={cls.id}
                name={cls.name}
                teacherName={teacherName}
                activeAssignments={cls.activeAssignments}
                image={cls.image}
              />
            );
          })}
        </div>
      )}
    </section>
  );
};
