/**
 * Unified API client — @hey-api/openapi-ts generated SDK
 * 
 * All server state access goes through this.
 * Do NOT import axios directly; use these typed functions.
 */
export {
  // Auth
  loginApiV1AuthLoginPost,
  registerApiV1AuthRegisterPost,

  // Users
  getCurrentUserProfileApiV1AuthMeGet,
  updateMeApiV1UsersMePatch,

  // Tests
  listMyTestsApiV1TestsGet,
  createTestApiV1TestsPost,
  getTestApiV1TestsTestIdGet,
  updateTestApiV1TestsTestIdPatch,
  deleteTestApiV1TestsTestIdDelete,
  addQuestionApiV1TestsTestIdQuestionsPost,
  updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch,
  deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete,

  // Catalog
  searchCatalogApiV1CatalogGet,
  getPublicTestApiV1CatalogTestIdGet,

  // Attempts
  startAttemptApiV1AttemptsPost,
  listMyAttemptsApiV1AttemptsGet,
  getActiveAttemptApiV1AttemptsActiveGet,
  getAttemptApiV1AttemptsAttemptIdGet,
  submitAnswerApiV1AttemptsAttemptIdAnswersPost,
  submitBulkAnswersApiV1AttemptsAttemptIdBulkAnswersPost,
  finishAttemptApiV1AttemptsAttemptIdFinishPost,
  getResultApiV1AttemptsAttemptIdResultGet,

  // Tags
  createTagApiV1TagsPost,
  listTagsApiV1TagsGet,

  // Stats
  getAuthorStatsApiV1StatsMeGet,
  getCalendarApiV1StatsCalendarGet,
  getTestStatsApiV1StatsTestsTestIdGet,

  // Media
  uploadMediaApiV1MediaUploadPost,

  // Types
  type Options,
} from './generated/sdk.gen'

export type {
  UserResponse,
  LoginRequest,
  UserCreate,
  TokenResponse,
  UserUpdate,
  ActiveAttemptResponse,
  TestResponse,
  TestDetailResponse,
  TestAuthorDetailResponse,
  TestCreate,
  TestUpdate,
  QuestionResponse,
  QuestionAuthorResponse,
  QuestionType,
  QuestionCreate,
  QuestionUpdate,
  OptionCreate,
  OptionResponse,
  OptionAuthorResponse,
  TagResponse,
  TagCreate,
  AttemptResponse,
  AttemptResultResponse,
  AttemptStartRequest,
  AnswerSubmitRequest,
  AttemptSummary,
  AuthorStatsResponse,
  CalendarResponse,
  PageAttemptSummary,
  TestStatsResponse,
  ErrorResponse,
} from './generated/types.gen'

// Re-export client for custom calls if needed
export { client } from './generated/client.gen'
