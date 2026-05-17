import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'
import {
  startAttemptApiV1AttemptsPost,
  submitAnswerApiV1AttemptsAttemptIdAnswersPost,
  finishAttemptApiV1AttemptsAttemptIdFinishPost,
  getResultApiV1AttemptsAttemptIdResultGet,
} from '@/shared/api/client/attempts'

export function useStartAttempt() {
  return useMutation({
    mutationFn: (testId: number) => startAttemptApiV1AttemptsPost({test_id: testId}),
  })
}

export function useSubmitAnswer(attemptId: number) {
  return useMutation({
    mutationFn: (data: Parameters<typeof submitAnswerApiV1AttemptsAttemptIdAnswersPost>[0]) => submitAnswerApiV1AttemptsAttemptIdAnswersPost({attemptId, ...data}),
  })
}

export function useFinishAttempt(attemptId: number) {
  return useMutation({
    mutationFn: () => finishAttemptApiV1AttemptsAttemptIdFinishPost({attemptId}),
  })
}

export function useAttemptResult(attemptId: number) {
  return useQuery({
    queryKey: ['attempts', attemptId, 'result'],
    queryFn: () => getResultApiV1AttemptsAttemptIdResultGet({attemptId}),
    enabled: !!attemptId,
  })
}
