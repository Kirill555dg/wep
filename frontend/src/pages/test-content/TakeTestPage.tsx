export default function TakeTestPage({ editMode = false }: { editMode?: boolean }) {
  return (
    <div>
      {editMode ? 'Edit Test (placeholder)' : 'Take Test (placeholder)'}
    </div>
  )
}
