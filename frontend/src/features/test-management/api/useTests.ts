import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'
import {
  addQuestionApiV1TestsTestIdQuestionsPost,
  createTestApiV1TestsPost,
  deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete,
  deleteTestApiV1TestsTestIdDelete,
  getTestApiV1TestsTestIdGet,
  listMyTestsApiV1TestsGet,
  updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch,
  updateTestApiV1TestsTestIdPatch,
} from '@/shared/api/client/tests'

export function useCreateTest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof createTestApiV1TestsPost>[0]) => createTestApiV1TestsPost(data),
    onSuccess: () => qc.invalidateQueries({queryKey: ['tests', 'my']}),
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
    onSuccess: () => qc.invalidateQueries({queryKey: ['tests', id]}),
  })
}

export function useDeleteTest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteTestApiV1TestsTestIdDelete({testId: id}),
    onSuccess: () => qc.invalidateQueries({queryKey: ['tests', 'my']}),
  })
}

export function useAddQuestion(testId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof addQuestionApiV1TestsTestIdQuestionsPost>[0]) => addQuestionApiV1TestsTestIdQuestionsPost({testId, ...data}),
    onSuccess: () => qc.invalidateQueries({queryKey: ['tests', testId]}),
  })
}

export function useUpdateQuestion(testId: number, questionId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch>[0]) => updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch({testId, questionId, ...data}),
    onSuccess: () => qc.invalidateQueries({queryKey: ['tests', testId]}),
  })
}

export function useDeleteQuestion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ testId, questionId }: { testId: number; questionId: number }) => deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete({testId, questionId}),
    onSuccess: (_data, variables) => qc.invalidateQueries({queryKey: ['tests', variables.testId]}),
  })
}
