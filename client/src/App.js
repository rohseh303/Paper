import TextEditor from "./TextEditor"
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom"
import HomePage from "./HomePage"

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact>
          <Redirect to="/documents" />
        </Route>
        <Route path="/documents/:id">
          <TextEditor />
        </Route>
        <Route path="/documents">
          <HomePage />
        </Route>
      </Switch>
    </Router>
  )
}

export default App
