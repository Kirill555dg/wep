import React, {useState} from 'react';
import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import * as z from 'zod';
import {Button} from '@/shared/ui/button';
import {Input} from '@/shared/ui/input';
import {Label} from '@/shared/ui/label';
import {Textarea} from '@/shared/ui/textarea';
import {Badge} from '@/shared/ui/badge';
import {Checkbox} from '@/shared/ui/checkbox';
import {X} from 'lucide-react';

const schema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().nullable().optional(),
  is_public: z.boolean().optional(),
  time_limit_minutes: z.number().min(1).nullable().optional(),
  tag_names: z.array(z.string()).optional(),
});

type FormValues = z.infer<typeof schema>;

interface TestMetaFormProps {
  defaultValues?: Partial<FormValues>;
  onSubmit: (values: FormValues) => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

export default function TestMetaForm({defaultValues, onSubmit, isLoading, mode = 'create'}: TestMetaFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: {errors},
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: defaultValues?.title ?? '',
      description: defaultValues?.description ?? null,
      is_public: defaultValues?.is_public ?? false,
      time_limit_minutes: defaultValues?.time_limit_minutes ?? null,
      tag_names: defaultValues?.tag_names ?? [],
    },
  });

  const tags = watch('tag_names') ?? [];
  const [tagInput, setTagInput] = useState('');

  const addTag = () => {
    const t = tagInput.trim();
    if (t && !tags.includes(t)) {
      setValue('tag_names', [...tags, t]);
      setTagInput('');
    }
  };

  const removeTag = (t: string) => {
    setValue('tag_names', tags.filter((tag) => tag !== t));
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input id="title" {...register('title')} />
        {errors.title && <p className="text-sm text-red-500">{errors.title.message}</p>}
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea id="description" {...register('description', {setValueAs: (v) => (v === '' ? null : v)})} />
      </div>

      <div className="flex items-center gap-3">
        <Checkbox
          id="is_public"
          checked={watch('is_public') ?? false}
          onCheckedChange={(v) => setValue('is_public', Boolean(v))}
        />
        <Label htmlFor="is_public">Public</Label>
      </div>

      <div>
        <Label htmlFor="time_limit_minutes">Time limit (minutes)</Label>
        <Input
          id="time_limit_minutes"
          type="number"
          {...register('time_limit_minutes', {setValueAs: (v) => (v === '' ? null : Number(v))})}
        />
      </div>

      <div>
        <Label htmlFor="tags">Tags</Label>
        <div className="flex gap-2 mt-1">
          <Input
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addTag();
              }
            }}
            placeholder="Type and press Enter"
          />
          <Button type="button" onClick={addTag} variant="outline">
            Add
          </Button>
        </div>
        <div className="flex flex-wrap gap-2 mt-2">
          {tags.map((t) => (
            <Badge key={t} variant="secondary" className="gap-1">
              {t}
              <button type="button" onClick={() => removeTag(t)} className="ml-1">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      </div>

      <div className="flex gap-2 pt-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Test' : 'Update Test'}
        </Button>
      </div>
    </form>
  );
}
