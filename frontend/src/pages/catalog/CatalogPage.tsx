import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { searchCatalogApiV1CatalogGet } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'
import type { TestResponse } from '@/shared/api'

export default function CatalogPage() {
  const [tests, setTests] = useState<TestResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTests()
  }, [])

  const loadTests = async () => {
    try {
      const response = await searchCatalogApiV1CatalogGet({ client })
      setTests(response.data || [])
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-center py-8">Загрузка...</div>
  if (error) return <div className="text-center py-8 text-red-600">{error}</div>

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Каталог тестов</h1>
      
      {tests.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Нет доступных тестов</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tests.map((test) => (
            <div key={test.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <h2 className="text-xl font-semibold mb-2">{test.title}</h2>
              <p className="text-gray-600 mb-4">{test.description || 'Нет описания'}</p>
              
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{test.questions_count} вопросов</span>
                {test.time_limit_minutes && <span>{test.time_limit_minutes} мин</span>}
              </div>

              <div className="flex gap-2">
                <Link to={`/tests/${test.id}`} className="flex-1 text-center py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Начать тест
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}