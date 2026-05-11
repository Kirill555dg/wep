import type { ClassInfo } from "./types"


export const mockClasses: ClassInfo[] = [
  {
    id: 1,
    name: "Математика 10А",
    subject: "Математика",
    description:
      "Курс по математике для учеников 10А класса. Включает алгебру, геометрию, тригонометрию и начала математического анализа.",
    schedule: "Понедельник, среда, пятница — 9:00–10:30",
    classroom: "Кабинет 305",
    entryCode: "MATH10A",
    teacherId: 1,
    activeAssignments: 3,
    image: "/class/math.jpg",
  },
  {
    id: 2,
    name: "Физика 10А",
    subject: "Физика",
    description: "Курс по физике с упором на эксперименты и практические задания.",
    schedule: "Вторник, четверг — 11:00–12:30",
    classroom: "Кабинет 310",
    entryCode: "PHYS10A",
    teacherId: 1,
    activeAssignments: 2,
    image: "/class/physics.jpg",
  },
]
