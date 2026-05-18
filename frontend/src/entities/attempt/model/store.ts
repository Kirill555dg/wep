import {create} from 'zustand'
import type {AttemptResponse, AnswerSubmitRequest} from '@/shared/api/client/testConstructorAPI.schemas'
import type {ATTEMPT_STATUS} from '@/shared/config/constants'

export interface Answer {
  questionId: number
  selectedOptionIds?: number[]
  textAnswer?: string
  isSubmitted: boolean
}

export interface Attempt {
  id: number
  testId: number
  userId: number
  status: typeof ATTEMPT_STATUS[keyof typeof ATTEMPT_STATUS]
  startedAt: string
  finishedAt?: string
  expiresAt?: string
  score?: number
  maxScore?: number
  answers: Record<number, Answer>
  currentQuestionIndex: number
  timeRemaining: number
}

interface AttemptState {
  currentAttempt: Attempt | null
  isSubmitting: boolean
  
  setCurrentAttempt: (attempt: Attempt | null) => void
  startAttempt: (testId: number, maxScore: number, timeLimit?: number) => void
  submitAnswer: (questionId: number, answer: AnswerSubmitRequest) => void
  navigateToQuestion: (index: number) => void
  updateTimeRemaining: (time: number) => void
  finishAttempt: () => void
  resetCurrentAttempt: () => void
}

const initialState = {
  currentAttempt: null,
  isSubmitting: false,
}

export const useAttemptStore = create<AttemptState>((set) => ({
  ...initialState,

  setCurrentAttempt: (attempt) => set({currentAttempt: attempt}),

  startAttempt: (testId, maxScore, timeLimit) => {
    const newAttempt: Attempt = {
      id: 0,
      testId,
      userId: 0,
      status: 'in_progress',
      startedAt: new Date().toISOString(),
      expiresAt: timeLimit 
        ? new Date(Date.now() + timeLimit * 60 * 1000).toISOString() 
        : undefined,
      maxScore,
      answers: {},
      currentQuestionIndex: 0,
      timeRemaining: timeLimit ? timeLimit * 60 : Infinity,
    }
    set({currentAttempt: newAttempt})
  },

  submitAnswer: (questionId, answer) => set((state) => {
    if (!state.currentAttempt) return state
    
    const newAnswers = {
      ...state.currentAttempt.answers,
      [questionId]: {
        questionId,
        selectedOptionIds: answer.selected_option_ids,
        textAnswer: answer.text_answer,
        isSubmitted: true,
      },
    }

    return {
      currentAttempt: {
        ...state.currentAttempt,
        answers: newAnswers,
      },
    }
  }),

  navigateToQuestion: (index) => set((state) => ({
    currentAttempt: state.currentAttempt 
      ? {...state.currentAttempt, currentQuestionIndex: index}
      : null,
  })),

  updateTimeRemaining: (time) => set((state) => ({
    currentAttempt: state.currentAttempt 
      ? {...state.currentAttempt, timeRemaining: time}
      : null,
  })),

  finishAttempt: () => set((state) => ({
    currentAttempt: state.currentAttempt 
      ? {
          ...state.currentAttempt,
          status: 'completed',
          finishedAt: new Date().toISOString(),
        }
      : null,
  })),

  resetCurrentAttempt: () => set({currentAttempt: null, isSubmitting: false}),
}))
