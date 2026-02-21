import { useState } from 'react'
import './App.css'
import DemoApp from './demo-site/DemoApp'
import Widget from './widget/Widget'

function App() {
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);

  return (
    <>
      <DemoApp isWidgetOpen={isWidgetOpen} />
      <Widget isOpen={isWidgetOpen} setIsOpen={setIsWidgetOpen} />
    </>
  )
}

export default App