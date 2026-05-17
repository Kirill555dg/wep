import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'
import {toast} from '@/shared/hooks/use-toast'
import {
  createTestApiV1TestsPost,
  listMyTestsApiV1TestsGet,
  getTestApiV1TestsTestIdGet,
  updateTestApiV1TestsTestIdPatch,
  deleteTestApiV1TestsTestIdDelete,
  addQuestionApiV1TestsTestIdQuestionsPost,
} from '@/shared/api/client/tests'

export function useCreateTest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof createTestApiV1TestsPost>[0]) => createTestApiV1TestsPost(data),
    onSuccess: () => {
      qc.invalidateQueries({queryKey: ['tests', 'my']})
      toast({title: 'Сохранено'})
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'})
    },
  })
}

export function useMyTests() {
  return useQuery({
    queryKey: ['tests', 'my'],
    queryFn: () => listMyTestsApiV1TestsGet(),
  })
}

export function useTestDetail(id: number) {
  return useQuery({
    queryKey: ['tests', id],
    queryFn: () => getTestApiV1TestsTestIdGet({testId: id}),
    enabled: !!id,
  })
}

export function useUpdateTest(id: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof updateTestApiV1TestsTestIdPatch>[0]) => updateTestApiV1TestsTestIdPatch({testId: id, ...data}),
    onSuccess: () => {
      qc.invalidateQueries({queryKey: ['tests', id]})
      toast({title: 'Сохранено'})
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'})
    },
  })
}

export function useDeleteTest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteTestApiV1TestsTestIdDelete({testId: id}),
    onSuccess: () => {
      qc.invalidateQueries({queryKey: ['tests', 'my']})
      toast({title: 'Удалено'})
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'})
    },
  })
}

export function useAddQuestion(testId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof addQuestionApiV1TestsTestIdQuestionsPost>[0]) => addQuestionApiV1TestsTestIdQuestionsPost({testId, ...data}),
    onSuccess: () => {
      qc.invalidateQueries({queryKey: ['tests', testId]})
      toast({title: 'Сохранено'})
    },
    onError: (e: any) => {
      toast({title: e.response?.data?.message || 'Ошибка', variant: 'destructive'})
    },
  })
}
