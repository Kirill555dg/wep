import { User } from "./types"

export const mockUsers: User[] = [
  {
    id: 1,
    firstName: "Иван",
    lastName: "Смирнов",
    middleName: "Александрович",
    email: "teacher@school.edu",
    role: "teacher",
    gender: "male",
    avatar: "/avatar/male3.png",
    phone: "+7 (999) 123-45-67",
    address: "г. Москва, ул. Примерная, д. 42",
    birthDate: "1982-03-15",
    about: "Преподаватель математики. Работаю в школе №123 более 10 лет.",
    contacts: {
      telegram: "https://t.me/example_DNnviJDfui",
      vk: "https://vk.com/example_DNnviJDfui",
    },
  },
  {
    id: 2,
    firstName: "Мария",
    lastName: "Смирнова",
    email: "student@school.edu",
    role: "student",
    gender: "female",
    avatar: "/avatar/female1.png",
    phone: "+7 (912) 555-12-12",
    address: "г. Екатеринбург, ул. Школьная, д. 7",
    birthDate: "2009-11-01",
    about: "Ученик 10А класса. Увлекаюсь физикой и веб-дизайном.",
    contacts: {
      telegram: "https://t.me/example_HXQWdiJDfu",
      vk: "https://vk.com/example_HXQWdiJDfu",
    },
  },
]
