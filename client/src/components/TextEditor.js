import React, { useCallback, useEffect, useState } from "react"
import Quill from "quill"
import "quill/dist/quill.snow.css"
import { io } from "socket.io-client"
import { useParams } from "react-router-dom"
import PopUp from "./PopUp"

const SAVE_INTERVAL_MS = 2000
const TOOLBAR_OPTIONS = [
  [{ header: [1, 2, 3, 4, 5, 6, false] }],
  [{ font: [] }],
  [{ list: "ordered" }, { list: "bullet" }],
  ["bold", "italic", "underline"],
  [{ color: [] }, { background: [] }],
  [{ script: "sub" }, { script: "super" }],
  [{ align: [] }],
  ["image", "blockquote", "code-block"],
  ["clean"],
]

export default function TextEditor() {
  const { id: documentId } = useParams()
  const [socket, setSocket] = useState()
  const [quill, setQuill] = useState()

  const [showPopup, setShowPopup] = useState(false)

  const [selectedText, setSelectedText] = useState("")
  const [suggestions, setSuggestions] = useState("")

  useEffect(() => {
    const s = io("http://localhost:3001")
    setSocket(s)

    return () => {
      s.disconnect()
    }
  }, [])

  // loading the document from the server
  useEffect(() => {
    if (socket == null || quill == null) return

    socket.on("load-document", document => {
      console.log("Document loaded:", document)
      quill.setContents(document)
      quill.enable()
    })

    socket.emit("get-document", documentId)

    return () => {
      socket.off("load-document")
    }
  }, [socket, quill, documentId])

  // saving the document to the server
  useEffect(() => {
    if (socket == null || quill == null) return

    const interval = setInterval(() => {
      socket.emit("save-document", quill.getContents(), documentId)
    }, SAVE_INTERVAL_MS)

    return () => {
      clearInterval(interval)
    }
  }, [socket, quill, documentId])

  // handling changes made by the user
  useEffect(() => {
    if (socket == null || quill == null) return

    const handler = delta => {
      quill.updateContents(delta)
    }
    socket.on("receive-changes", handler)

    return () => {
      socket.off("receive-changes", handler)
    }
  }, [socket, quill])

    // user makes changes and sends them to the server
  useEffect(() => {
    if (socket == null || quill == null) return

    const handler = (delta, oldDelta, source) => {
      if (source !== "user") return
      socket.emit("send-changes", delta, documentId)
    }
    quill.on("text-change", handler)

    return () => {
      quill.off("text-change", handler)
    }
  }, [socket, quill, documentId])

  // user highlights text and shows the popup
  useEffect(() => {
    if (quill == null) return

    const handleSelectionChange = (range, oldRange, source) => {
      if (showPopup) return

      if (source !== "user" || range == null || range.length === 0) {
        setShowPopup(false)
        return
      }

      console.log("Selection changed:", range, oldRange, source)
      const text = quill.getText(range.index, range.length)
      console.log("Selected text:", text)
      setSelectedText(text)
      // instead of setting text to a state variable, save the selected text to the document object
      setShowPopup(true)
    }

    quill.on("selection-change", handleSelectionChange)

    return () => {
      quill.off("selection-change", handleSelectionChange)
    }
  }, [quill, showPopup])

    // handling received text suggestions from the server
    useEffect(() => {
      if (socket == null) return
  
      const handler = (data) => {
        console.log("Received suggestions:", data.suggestions)
        setSuggestions(data.suggestions) // Update state with received suggestions
      }
      socket.on("text-suggestion", handler)
  
      return () => {
        socket.off("text-suggestion", handler)
      }
    }, [socket])

  const wrapperRef = useCallback(wrapper => {
    if (wrapper == null) return

    wrapper.innerHTML = ""
    const editor = document.createElement("div")
    wrapper.append(editor)
    const q = new Quill(editor, {
      theme: "snow",
      modules: { toolbar: TOOLBAR_OPTIONS },
    })
    q.disable()
    q.setText("Loading file...")
    setQuill(q)
  }, [])

  return (
    <div className="container" ref={wrapperRef}>
      {showPopup && (
        <PopUp showPopup={showPopup} setShowPopup={setShowPopup} socket={socket} selectedText={selectedText} documentId={documentId}/>
      )}
      {suggestions && (
        <div className="suggestions">
          <h3>Suggestions:</h3>
          <p>{suggestions}</p>
        </div>
      )}
    </div>
  )
}
