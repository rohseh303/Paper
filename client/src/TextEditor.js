import React, { useCallback, useEffect, useState } from "react"
import Quill from "quill"
import "quill/dist/quill.snow.css"
import { io } from "socket.io-client"
import { useParams } from "react-router-dom"

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
  const [desiredChange, setDesiredChange] = useState("")

  useEffect(() => {
    const s = io("http://localhost:3001")
    setSocket(s)

    return () => {
      s.disconnect()
    }
  }, [])

  useEffect(() => {
    if (socket == null || quill == null) return

    socket.once("load-document", document => {
      console.log("Document loaded:", document)
      quill.setContents(document)
      quill.enable()
    })

    socket.emit("get-document", documentId)
  }, [socket, quill, documentId])

  useEffect(() => {
    if (socket == null || quill == null) return

    const interval = setInterval(() => {
      socket.emit("save-document", quill.getContents(), documentId)
    }, SAVE_INTERVAL_MS)

    return () => {
      clearInterval(interval)
    }
  }, [socket, quill, documentId])

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

  useEffect(() => {
    if (quill == null) return

    const handleSelectionChange = (range, oldRange, source) => {
      console.log("Selection changed:", range, oldRange, source)
      
      if (showPopup) return

      if (source !== "user" || range == null || range.length === 0) {
        setShowPopup(false)
        return
      }

      const text = quill.getText(range.index, range.length)
      console.log("Selected text:", text)
      setSelectedText(text)
      setShowPopup(true)
    }

    quill.on("selection-change", handleSelectionChange)

    return () => {
      quill.off("selection-change", handleSelectionChange)
    }
  }, [quill, showPopup])

  const handleSubmit = () => {
    // Send the selected text and desired change to the server
    socket.emit("text-selection", { text: selectedText, changes: desiredChange, documentId })
    setShowPopup(false)
    setDesiredChange("")
  }

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
    q.setText("Loading...")
    setQuill(q)
  }, [])

  return (
    <div className="container" ref={wrapperRef}>
      {showPopup && (
        <div className="popup">
          <h3>Enter Desired Change</h3>
          <textarea
            value={desiredChange}
            onChange={(e) => setDesiredChange(e.target.value)}
            placeholder="Describe the changes you'd like to see..."
          />
          <button onClick={handleSubmit}>Submit</button>
          <button onClick={() => setShowPopup(false)}>Cancel</button>
        </div>
      )}
    </div>
  )
}
