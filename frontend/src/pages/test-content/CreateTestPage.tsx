import { useState, useEffect, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Infinity, X } from 'lucide-react'

import { createTestApiV1TestsPost, listTagsApiV1TagsGet, client } from '@/shared/api'
import type { TestCreate } from '@/shared/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { RadioGroup, RadioGroupItem } from '@/shared/ui/radio-group'
import { Switch } from '@/shared/ui/switch'
import { Badge } from '@/shared/ui/badge'
import { useAuth } from '@/shared/hooks/useAuth'
import { useToast } from '@/shared/hooks/useToast'
import { getApiError } from '@/shared/lib/api-error'

const schema = z.object({
  title: z.string().min(1, 'Обязательное поле').max(255),
  description: z.string().optional(),
  is_public: z.boolean(),
  track_time: z.boolean(),
  time_limit_minutes: z.number().nullable().optional(),
  attempt_limit: z.number().min(1).nullable().optional(),
  tag_names: z.array(z.string()),
  completion_message: z.string().nullable().optional(),
})

type FormData = z.infer<typeof schema>

export default function CreateTestPage() {
  const navigate = useNavigate()
  const { isAuthed, requireAuth } = useAuth()
  const { success: toastSuccess, error: toastError } = useToast()
  const [tagInput, setTagInput] = useState('')
  const [showTagDropdown, setShowTagDropdown] = useState(false)

  useEffect(() => {
    requireAuth('/tests/new/edit')
  }, [requireAuth])

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: '',
      description: '',
      is_public: false,
      track_time: true,
      time_limit_minutes: null,
      attempt_limit: null,
      tag_names: [],
      completion_message: null,
    },
  })

  const trackTime = watch('track_time')
  const tagNames = watch('tag_names') ?? []

  useEffect(() => {
    if (!trackTime) {
      setValue('time_limit_minutes', null)
    }
  }, [trackTime, setValue])

  const [allTags, setAllTags] = useState<Array<{ id: number; name: string }>>([])

  useEffect(() => {
    if (!isAuthed) return
    listTagsApiV1TagsGet({ client }).then((res) => {
      const data = (res.data ?? []) as Array<{ id: number; name: string }>
      setAllTags(data)
    })
  }, [isAuthed])

  const createMutation = useMutation({
    mutationFn: (body: TestCreate) =>
      createTestApiV1TestsPost({ client, body }),
    onSuccess: (res) => {
      toastSuccess('Тест создан')
      navigate(`/tests/${res.data!.id}/edit`)
    },
    onError: (err) => {
      const { message } = getApiError(err)
      toastError(message)
    },
  })

  const onSubmit = (data: FormData) => {
    const body: TestCreate = {
      title: data.title,
      description: data.description || null,
      is_public: false,
      track_time: data.track_time,
      time_limit_minutes: data.track_time ? data.time_limit_minutes ?? null : null,
      attempt_limit: data.attempt_limit ?? null,
      tag_names: data.tag_names,
      completion_message: data.completion_message || null,
    }
    createMutation.mutate(body)
  }

  const addTag = (name: string) => {
    const trimmed = name.trim()
    if (!trimmed) return
    if (!tagNames.includes(trimmed)) {
      setValue('tag_names', [...tagNames, trimmed])
    }
    setTagInput('')
    setShowTagDropdown(false)
  }

  const removeTag = (name: string) => {
    setValue('tag_names', tagNames.filter((t) => t !== name))
  }

  const filteredTags = useMemo(() => {
    if (!tagInput.trim()) return []
    const lower = tagInput.toLowerCase()
    return allTags.filter(
      (t) =>
        t.name.toLowerCase().includes(lower) && !tagNames.includes(t.name),
    )
  }, [tagInput, allTags, tagNames])

  if (!isAuthed) return null

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <Button variant="ghost" asChild className="mb-4 pl-0">
        <Link to="/my-tests">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Назад к моим тестам
        </Link>
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Новый тест</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Global validation summary */}
            {Object.keys(errors).length > 0 && (
              <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 space-y-1">
                <p className="font-semibold">Исправьте ошибки:</p>
                {Object.entries(errors).map(([key, err]) => (
                  <p key={key}>
                    {key}: {String(err?.message || 'неверное значение')}
                  </p>
                ))}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">Название</Label>
              <Input id="title" {...register('title')} placeholder="Название теста" />
              {errors.title && (
                <p className="text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Описание</Label>
              <Textarea
                id="description"
                rows={4}
                {...register('description')}
                placeholder="Описание теста"
              />
            </div>

            <hr className="border-t" />

            <div className="space-y-2">
              <Label>Видимость</Label>
              <Controller
                name="is_public"
                control={control}
                render={({ field }) => (
                  <RadioGroup
                    value={field.value ? 'public' : 'private'}
                    onValueChange={(v) => field.onChange(v === 'public')}
                    className="flex gap-4"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="public" id="public" />
                      <Label htmlFor="public" className="cursor-pointer">Публичный</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="private" id="private" />
                      <Label htmlFor="private" className="cursor-pointer">Приватный</Label>
                    </div>
                  </RadioGroup>
                )}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="track_time">Отслеживать время</Label>
                <Controller
                  name="track_time"
                  control={control}
                  render={({ field }) => (
                    <Switch
                      id="track_time"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  )}
                />
              </div>
            </div>

            {trackTime && (
              <div className="space-y-2">
                <Label htmlFor="time_limit_minutes">Лимит времени (минуты)</Label>
                <Input
                  id="time_limit_minutes"
                  type="number"
                  min={1}
                  {...register('time_limit_minutes', {
                    setValueAs: (v) => (v === '' ? null : Number(v)),
                  })}
                  placeholder="Без ограничения"
                />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="attempt_limit">Лимит попыток</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="attempt_limit"
                  type="number"
                  min={1}
                  {...register('attempt_limit', {
                    setValueAs: (v) => (v === '' ? null : Number(v)),
                  })}
                  placeholder="Без ограничения"
                  className="w-32"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  title="Без ограничения"
                  onClick={() => setValue('attempt_limit', null)}
                >
                  <Infinity className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <hr className="border-t" />

            <div className="space-y-2">
              <Label>Теги</Label>
              <div className="flex flex-wrap gap-2">
                {tagNames.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button type="button" onClick={() => removeTag(tag)} className="ml-1 hover:text-red-600">
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
              <div className="relative">
                <Input
                  value={tagInput}
                  onChange={(e) => {
                    setTagInput(e.target.value)
                    setShowTagDropdown(true)
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ',') {
                      e.preventDefault()
                      addTag(tagInput)
                    }
                  }}
                  onBlur={() => {
                    setTimeout(() => setShowTagDropdown(false), 150)
                  }}
                  placeholder="Введите тег и нажмите Enter"
                />
                {showTagDropdown && filteredTags.length > 0 && (
                  <div className="absolute z-10 w-full bg-white border rounded-md shadow-lg mt-1 max-h-40 overflow-auto">
                    {filteredTags.map((tag) => (
                      <button
                        key={tag.id}
                        type="button"
                        onMouseDown={(e) => {
                          e.preventDefault()
                          addTag(tag.name)
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm"
                      >
                        {tag.name}
                      </button>
                    ))}
                  </div>
                )}
                {showTagDropdown &&
                  tagInput.trim() &&
                  !filteredTags.some(
                    (t) => t.name.toLowerCase() === tagInput.trim().toLowerCase(),
                  ) &&
                  !tagNames.includes(tagInput.trim()) && (
                    <div className="absolute z-10 w-full bg-white border rounded-md shadow-lg mt-1">
                      <button
                        type="button"
                        onMouseDown={(e) => {
                          e.preventDefault()
                          addTag(tagInput)
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm text-muted-foreground"
                      >
                        Создать тег "{tagInput.trim()}"
                      </button>
                    </div>
                  )}
              </div>
            </div>

            <hr className="border-t" />

            <div className="space-y-2">
              <Label htmlFor="completion_message">Сообщение по завершении</Label>
              <Textarea
                id="completion_message"
                rows={3}
                {...register('completion_message')}
                placeholder={`Доступные переменные: #score, #max, #percent\nПример: Поздравляем! Вы набрали #score из #max баллов.`}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting || createMutation.isPending}
            >
              {createMutation.isPending ? 'Создание...' : 'Создать черновик'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
