/**
 * Editor for a single question within a test.
 */
import {useState, useEffect} from 'react'
import {useForm} from 'react-hook-form'
import {zodResolver} from '@hookform/resolvers/zod'
import * as z from 'zod'
import {QuestionType} from '@/shared/api/client/testConstructorAPI.schemas'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Label} from '@/shared/ui/label'
import {Textarea} from '@/shared/ui/textarea'
import {Checkbox} from '@/shared/ui/checkbox'
import {Badge} from '@/shared/ui/badge'
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/shared/ui/select'
import {Card} from '@/shared/ui/card'

const optionSchema = z.object({
  text: z.string().min(1),
  is_correct: z.boolean(),
  order_number: z.number().int().default(0),
})

const questionSchema = z.object({
  question_type: z.nativeEnum(QuestionType),
  text: z.string().min(1, 'Условие обязательно'),
  order_number: z.number().int().default(0),
  points: z.number().int().min(1).default(1),
  explanation: z.string().nullable(),
  correct_answer: z.string().nullable(),
  image_url: z.string().nullable(),
  options: z.array(optionSchema).default([]),
})

export type QuestionFormData = z.infer<typeof questionSchema>

interface QuestionEditorWidgetProps {
  initialData?: QuestionFormData
  onSave: (data: QuestionFormData) => void
  onCancel: () => void
}

export default function QuestionEditorWidget({initialData, onSave, onCancel}: QuestionEditorWidgetProps) {
  const [preview, setPreview] = useState(false)

  const {register, handleSubmit, watch, setValue, formState: {errors}} = useForm<QuestionFormData>({
    resolver: zodResolver(questionSchema),
    defaultValues: initialData || {
      question_type: QuestionType.SINGLE_CHOICE,
      text: '',
      points: 1,
      explanation: null,
      correct_answer: null,
      image_url: null,
      options: [],
    },
  })

  const type = watch('question_type')
  const options = watch('options') || []

  const addOption = () => {
    setValue('options', [...options, {text: '', is_correct: false, order_number: options.length}])
  }

  const removeOption = (idx: number) => {
    setValue('options', options.filter((_, i) => i !== idx))
  }

  const updateOption = (idx: number, patch: Partial<typeof options[0]>) => {
    const next = options.map((o, i) => (i === idx ? {...o, ...patch} : o))
    setValue('options', next)
  }

  return (
    <Card className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{initialData ? 'Редактировать вопрос' : 'Новый вопрос'}</h3>
        <Button variant="ghost" size="sm" onClick={onCancel}>Отмена</Button>
      </div>

      <form onSubmit={handleSubmit(onSave)} className="space-y-4">
        <div>
          <Label>Тип вопроса</Label>
          <Select value={type} onValueChange={(v) => setValue('question_type', v as QuestionType)}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value={QuestionType.SINGLE_CHOICE}>Один вариант</SelectItem>
              <SelectItem value={QuestionType.MULTIPLE_CHOICE}>Несколько вариантов</SelectItem>
              <SelectItem value={QuestionType.TEXT_INPUT}>Свободный ответ</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Условие (Typst)</Label>
          <Textarea rows={5} {...register('text')} />
          {errors.text && <p className="text-red-500 text-sm">{errors.text.message}</p>}
          <Button type="button" variant="outline" size="sm" className="mt-1" onClick={() => setPreview(s => !s)}>{preview ? 'Скрыть' : 'Предпросмотр'}</Button>
          {preview && (
            <div className="mt-2 border rounded p-2 bg-white">
              {/* TypstPreview lazy */}
              <p className="text-muted-foreground text-sm">Предпросмотр Typst будет здесь</p>
            </div>
          )}
        </div>

        <div>
          <Label>Баллы</Label>
          <Input type="number" {...register('points', {valueAsNumber: true})} />
        </div>

        {(type === QuestionType.SINGLE_CHOICE || type === QuestionType.MULTIPLE_CHOICE) && (
          <div className="space-y-2">
            <Label>Варианты ответа</Label>
            {options.map((opt, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <Checkbox checked={opt.is_correct} onCheckedChange={(v) => updateOption(idx, {is_correct: Boolean(v)})} />
                <Input value={opt.text} onChange={(e) => updateOption(idx, {text: e.target.value})} placeholder={`Вариант ${idx + 1}`} className="flex-1" />
                <Button type="button" variant="ghost" size="sm" onClick={() => removeOption(idx)}>×</Button>
              </div>
            ))}
            <Button type="button" variant="outline" size="sm" onClick={addOption}>+ Добавить вариант</Button>
          </div>
        )}

        {type === QuestionType.TEXT_INPUT && (
          <div>
            <Label>Правильный ответ</Label>
            <Input {...register('correct_answer')} placeholder="Текст правильного ответа" />
          </div>
        )}

        <div>
          <Label>Объяснение (Typst)</Label>
          <Textarea rows={3} {...register('explanation')} placeholder="Пояснение к правильному ответу" />
        </div>

        <div>
          <Label>URL изображения</Label>
          <Input {...register('image_url')} placeholder="http://..." />
        </div>

        <div className="flex gap-2">
          <Button type="submit">Сохранить</Button>
          <Button type="button" variant="ghost" onClick={onCancel}>Отмена</Button>
        </div>
      </form>
    </Card>
  )
}
