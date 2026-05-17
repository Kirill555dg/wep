import {create} from 'zustand';
import {QuestionAuthorResponse} from '@/shared/api/client/testConstructorAPI.schemas';

interface QuestionEditorState {
  questions: QuestionAuthorResponse[];
  setQuestions: (q: QuestionAuthorResponse[]) => void;
  activeQuestionId: number | null;
  setActiveQuestion: (id: number | null) => void;
  addQuestion: (q: QuestionAuthorResponse) => void;
  updateQuestion: (id: number, patch: Partial<QuestionAuthorResponse>) => void;
  removeQuestion: (id: number) => void;
}

export const useQuestionEditorStore = create<QuestionEditorState>((set, get) => ({
  questions: [],
  setQuestions: (questions) => set({questions}),
  activeQuestionId: null,
  setActiveQuestion: (activeQuestionId) => set({activeQuestionId}),
  addQuestion: (q) => set({questions: [...get().questions, q]}),
  updateQuestion: (id, patch) =>
    set({
      questions: get().questions.map((q) => (q.id === id ? {...q, ...patch} : q)),
    }),
  removeQuestion: (id) =>
    set({questions: get().questions.filter((q) => q.id !== id)}),
}));
