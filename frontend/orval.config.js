/**
 * Orval configuration for generating TanStack Query hooks and Axios client
 */
module.exports = {
  'test-constructor-api': {
    input: {
      target: './src/shared/api/openapi.json',
    },
    output: {
      target: './src/shared/api/client',
      client: 'react-query',
      mode: 'tags',
      override: {
        mutator: {
          path: './src/shared/api/axios.ts',
          name: 'request',
        },
        query: {
          useQuery: true,
          useInfinite: false,
          useMutation: true,
        },
      },
    },
  },
};
