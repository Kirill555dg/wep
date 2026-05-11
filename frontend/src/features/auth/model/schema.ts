import { z } from "zod"

export const loginSchema = z.object({
  email: z.string().email("Введите корректный email"),
  password: z.string().min(6, "Минимум 6 символов"),
  rememberMe: z.boolean().optional(),
})

export type LoginData = z.infer<typeof loginSchema>

export const resetPasswordSchema = z.object({
  email: z.string().email("Введите корректный email"),
})

export type ResetPasswordData = z.infer<typeof resetPasswordSchema>

export const registerSchema = z.object({
  lastName: z.string().min(1, "Введите фамилию"),
  firstName: z.string().min(1, "Введите имя"),
  middleName: z.string().optional(),

  email: z.string().email("Введите корректный email"),

  password: z.string().min(6, "Пароль должен содержать минимум 6 символов"),
  confirmPassword: z.string(),

  dateOfBirth: z.string().optional(),

  description: z.string().max(500, "Максимум 500 символов").optional(),

  agreeTerms: z.boolean().refine((v) => v === true, {
    message: "Необходимо согласие с условиями использования",
  }),
  role: z.enum(["student", "teacher"], {
    required_error: "Выберите роль",
  }),
  gender: z.enum(["male", "female"], {
    required_error: "Выберите пол",
  }),
}).refine((data) => data.password === data.confirmPassword, {
  path: ["confirmPassword"],
  message: "Пароли не совпадают",
})

export type RegisterData = z.infer<typeof registerSchema>
