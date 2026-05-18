import React, { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Infinity, X } from 'lucide-react'

import {
  getTestApiV1TestsTestIdGet,
  updateTestApiV1TestsTestIdPatch,
  deleteTestApiV1TestsTestIdDelete,
  listTagsApiV1TagsGet,
  client,
} from '@/shared/api'
import type { TestUpdate } from '@/shared/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import { RadioGroup, RadioGroupItem } from '@/shared/ui/radio-group'
import { Switch } from '@/shared/ui/switch'
import { Badge } from '@/shared/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/shared/ui/dialog'
import { useAuth } from '@/shared/hooks/useAuth'
import { useToast } from '@/shared/hooks/useToast'
import { getApiError } from '@/shared/lib/api-error'

const schema = z.object({
  title: z.string().min(1, 'Обязательное поле').max(255),
  description: z.string().optional(),
  is_public: z.boolean(),
  track_time: z.boolean(),
  time_limit_minutes: z.number().min(1).nullable().optional(),
  attempt_limit: z.number().min(1).nullable().optional(),
  tag_names: z.array(z.string()),
  completion_message: z.string().nullable().optional(),
  image_url: z.string().url('Некорректный URL').nullable().optional(),
})

type FormData = z.infer<typeof schema>

function SkeletonForm() {
  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3" />
      <div className="h-10 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/4" />
      <div className="h-24 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
      <div className="h-10 bg-gray-200 rounded animate-pulse" />
      <div className="h-10 bg-gray-200 rounded animate-pulse" />
    </div>
  )
}

export default function TestSettingsPage() {
  const { testId } = useParams<{ testId: string }>()
  const navigate = useNavigate()
  const { user, isAuthed, requireAuth } = useAuth()
  const { success: toastSuccess, error: toastError } = useToast()
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [tagInput, setTagInput] = useState('')
  const [showTagDropdown, setShowTagDropdown] = useState(false)

  const numTestId = Number(testId)

  useEffect(() => {
    requireAuth(`/tests/${testId}/settings`)
  }, [requireAuth, testId])

  const { data: test, isLoading } = useQuery({
    queryKey: ['test', testId],
    queryFn: () =>
      getTestApiV1TestsTestIdGet({ client, path: { test_id: numTestId } }),
    enabled: isAuthed,
  })

  const { data: allTagsResponse } = useQuery({
    queryKey: ['tags'],
    queryFn: () => listTagsApiV1TagsGet({ client }),
    enabled: isAuthed,
  })

  const allTags = allTagsResponse?.data ?? []

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    reset,
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
      image_url: null,
    },
  })

  const testData = test?.data

  useEffect(() => {
    if (testData) {
      reset({
        title: testData.title,
        description: testData.description ?? '',
        is_public: testData.is_public,
        track_time: (testData as Record<string, unknown>).track_time as boolean,
        time_limit_minutes: (testData as Record<string, unknown>)
          .time_limit_minutes as number | null | undefined,
        attempt_limit: (testData as Record<string, unknown>).attempt_limit as
          | number
          | null
          | undefined,
        tag_names:
          ((testData as Record<string, unknown>).tags as Array<{ name: string }> | undefined)?.map(
            (t) => t.name,
          ) ?? [],
        completion_message: (testData as Record<string, unknown>)
          .completion_message as string | null | undefined,
        image_url: (testData as Record<string, unknown>)
          .image_url as string | null | undefined,
      })
    }
  }, [testData, reset])

  const isPublic = watch('is_public')
  const trackTime = watch('track_time')
  const tagNames = watch('tag_names') ?? []

  useEffect(() => {
    const sub = watch((value, { name }) => {
      if (name === 'is_public') {
        if (value.is_public) {
          setValue('attempt_limit', null)
        } else {
          setValue('attempt_limit', 1)
        }
      }
    })
    return () => sub.unsubscribe()
  }, [watch, setValue])

  const saveMutation = useMutation({
    mutationFn: (body: TestUpdate) =>
      updateTestApiV1TestsTestIdPatch({
        client,
        path: { test_id: numTestId },
        body,
      }),
    onSuccess: () => {
      toastSuccess('Сохранено')
      navigate(`/tests/${testId}`)
    },
    onError: (err) => {
      const { message } = getApiError(err)
      toastError(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () =>
      deleteTestApiV1TestsTestIdDelete({
        client,
        path: { test_id: numTestId },
      }),
    onSuccess: () => {
      navigate('/my-tests')
    },
    onError: (err) => {
      const { message } = getApiError(err)
      toastError(message)
    },
  })

  const onSubmit = (data: FormData) => {
    const body: TestUpdate = {
      title: data.title,
      description: data.description || null,
      is_public: data.is_public,
      track_time: data.track_time,
      time_limit_minutes: data.track_time ? data.time_limit_minutes ?? null : null,
      attempt_limit: data.attempt_limit ?? null,
      tag_names: data.tag_names,
      completion_message: data.completion_message || null,
      image_url: data.image_url || null,
    }
    saveMutation.mutate(body)
  }

  const handleDelete = () => {
    deleteMutation.mutate()
    setDeleteDialogOpen(false)
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
    setValue(
      'tag_names',
      tagNames.filter((t) => t !== name),
    )
  }

  const filteredTags = useMemo(() => {
    if (!tagInput.trim()) return []
    const lower = tagInput.toLowerCase()
    return allTags.filter(
      (t) =>
        t.name.toLowerCase().includes(lower) && !tagNames.includes(t.name),
    )
  }, [tagInput, allTags, tagNames])

  if (!isAuthed) {
    return null
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-6">
        <SkeletonForm />
      </div>
    )
  }

  if (testData && (testData as Record<string, unknown>).author_id !== user?.id) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <p className="text-lg font-semibold mb-4">Нет доступа</p>
        <Button variant="outline" asChild>
          <Link to={`/tests/${testId}`}>← Назад к тесту</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      <Button variant="ghost" asChild className="mb-4 pl-0">
        <Link to={`/tests/${testId}`}>
          <ArrowLeft className="w-4 h-4 mr-1" />
          Назад к тесту
        </Link>
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>Настройки теста</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Название</Label>
              <Input
                id="title"
                {...register('title')}
                placeholder="Название теста"
              />
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

            <div className="space-y-2">
              <Label htmlFor="image_url">URL обложки</Label>
              <Input
                id="image_url"
                {...register('image_url')}
                placeholder="https://example.com/image.jpg"
              />
              {errors.image_url && (
                <p className="text-sm text-red-600">{errors.image_url.message}</p>
              )}
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
                      <Label htmlFor="public" className="cursor-pointer">
                        Публичный
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="private" id="private" />
                      <Label htmlFor="private" className="cursor-pointer">
                        Приватный
                      </Label>
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
                <Label htmlFor="time_limit_minutes">
                  Лимит времени (минуты)
                </Label>
                <Input
                  id="time_limit_minutes"
                  type="number"
                  min={1}
                  {...register('time_limit_minutes', {
                    setValueAs: (v) => (v === '' ? null : Number(v)),
                  })}
                  placeholder="Без ограничения"
                />
                {errors.time_limit_minutes && (
                  <p className="text-sm text-red-600">
                    {errors.time_limit_minutes.message}
                  </p>
                )}
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
              {errors.attempt_limit && (
                <p className="text-sm text-red-600">
                  {errors.attempt_limit.message}
                </p>
              )}
            </div>

            <hr className="border-t" />

            <div className="space-y-2">
              <Label>Теги</Label>
              <div className="flex flex-wrap gap-2">
                {tagNames.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-red-600"
                    >
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
              <Label htmlFor="completion_message">
                Сообщение по завершении
              </Label>
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
              disabled={isSubmitting || saveMutation.isPending}
            >
              {saveMutation.isPending ? 'Сохранение...' : 'Сохранить изменения'}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t text-center">
            <Button
              type="button"
              variant="link"
              className="text-red-600 hover:text-red-700"
              onClick={() => setDeleteDialogOpen(true)}
            >
              Удалить тест
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить тест?</DialogTitle>
            <DialogDescription>
              Это действие нельзя отменить. Тест будет удален навсегда.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Удаление...' : 'Удалить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
