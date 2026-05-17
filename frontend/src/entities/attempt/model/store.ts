import {create} from 'zustand';
import {AttemptResponse} from '@/shared/api/client/testConstructorAPI.schemas';

interface AttemptState {
  currentAttempt: AttemptResponse | null;
  setCurrentAttempt: (a: AttemptResponse | null) => void;
  answers: Record<number, {selectedOptionIds?: number[]; textAnswer?: string}>;
  setAnswer: (questionId: number, payload: {selectedOptionIds?: number[]; textAnswer?: string}) => void;
  clearAttempt: () => void;
}

export const useAttemptStore = create<AttemptState>((set) => ({
  currentAttempt: null,
  setCurrentAttempt: (currentAttempt) => set({currentAttempt}),
  answers: {},
  setAnswer: (questionId, payload) =>
    set((state) => ({
      answers: {...state.answers, [questionId]: payload},
    })),
  clearAttempt: () => set({currentAttempt: null, answers: {}}),
}));
