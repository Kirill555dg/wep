import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import CatalogPage from '@/pages/catalog/CatalogPage'

describe('CatalogPage E2E', () => {
  beforeEach(() => {
    cy.visit('/catalog')
  })

  it('loads catalog page', () => {
    cy.contains('Каталог тестов').should('be.visible')
  })

  it('search tests', () => {
    cy.get('[placeholder*="Поиск"]').type('математика')
    cy.contains('Основы математического анализа').should('be.visible')
  })
})
