import {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import {zodResolver} from '@hookform/resolvers/zod'
import {z} from 'zod'

import {useAuth} from '@/shared/hooks/useAuth'
import {useToast} from '@/shared/hooks/useToast'
import {getApiError} from '@/shared/lib/api-error'
import {uploadMediaApiV1MediaUploadPost, client} from '@/shared/api'
import {Button} from '@/shared/ui/button'
import {Card, CardContent} from '@/shared/ui/card'
import {Input} from '@/shared/ui/input'
import {Label} from '@/shared/ui/label'

import {ProfileAvatarBlock} from './ui/ProfileAvatarBlock'

const schema = z.object({
  first_name: z.string().min(1, 'Обязательное поле'),
  last_name: z.string().min(1, 'Обязательное поле'),
  middle_name: z.string().optional(),
  username: z.string().min(3, 'Минимум 3 символа'),
  email: z.string().email('Неверный email'),
})

type FormData = z.infer<typeof schema>

export default function ProfilePage() {
  const navigate = useNavigate()
  const {user, logout} = useAuth()
  const {info, error} = useToast()
  const [avatarPreview, setAvatarPreview] = useState<string | undefined>()
  const [uploading, setUploading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: {errors, isSubmitting},
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      first_name: user?.first_name ?? '',
      last_name: user?.last_name ?? '',
      middle_name: user?.middle_name ?? '',
      username: user?.username ?? '',
      email: user?.email ?? '',
    },
  })

  const onSubmit = async () => {
    // NOTE: updateUserMeApiV1UsersMePatch is not yet available in the generated SDK.
    info('Обновление профиля пока недоступно')
  }

  const handleAvatarSelect = async (file: File) => {
    setUploading(true)
    try {
      const res = await uploadMediaApiV1MediaUploadPost({
        client,
        body: {file} as any,
      })
      const url =
        (res as any).data?.url || (res as any).url || ''
      if (url) setAvatarPreview(url)
      // NOTE: updateUserMeApiV1UsersMePatch is not yet available in the generated SDK.
      info('Аватар загружен, но обновление профиля пока недоступно')
    } catch (err) {
      const apiErr = getApiError(err)
      error(apiErr.message || 'Ошибка загрузки аватара')
    } finally {
      setUploading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/catalog')
  }

  const initials = [user?.first_name, user?.last_name]
    .map((n) => n?.[0])
    .join('')
    .toUpperCase()

  if (!user) return null

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Профиль</h1>

      <Card>
        <CardContent className="p-6 flex flex-col items-center">
          <ProfileAvatarBlock
            initials={initials}
            previewUrl={avatarPreview}
            onSelect={handleAvatarSelect}
            disabled={uploading}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">Имя</Label>
              <Input id="first_name" {...register('first_name')} />
              {errors.first_name && (
                <p className="text-sm text-red-500">{errors.first_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="last_name">Фамилия</Label>
              <Input id="last_name" {...register('last_name')} />
              {errors.last_name && (
                <p className="text-sm text-red-500">{errors.last_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="middle_name">Отчество</Label>
              <Input id="middle_name" {...register('middle_name')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Имя пользователя</Label>
              <Input id="username" {...register('username')} />
              {errors.username && (
                <p className="text-sm text-red-500">{errors.username.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register('email')} />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full">
              Сохранить изменения
            </Button>
          </form>
        </CardContent>
      </Card>

      <Button variant="outline" onClick={handleLogout} className="w-full">
        Выйти
      </Button>
    </div>
  )
}
