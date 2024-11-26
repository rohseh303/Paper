import TextEditor from "./components/TextEditor"
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom"
import HomePage from "./components/HomePage/HomePage"

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/documents/:id" render={({ match }) => {
          debugger;
          return <TextEditor />;
        }} />
        <Route path="/documents" render={({ location }) => {
          debugger;
          return <HomePage />;
        }} />
        <Route path="*">
          <Redirect to="/documents" />
        </Route>
      </Switch>
    </Router>
  )
}

export default App
