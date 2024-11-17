import React, { useState } from "react"

const PopUp = ({showPopup, setShowPopup, socket, selectedText, documentId}) => {

const [desiredChange, setDesiredChange] = useState("")

    // handling text selection and sending it to the server
    const handleSubmit = () => {
        // Send the selected text and desired change to the server
        // console.log("Sending text selection:", selectedText, desiredChange, documentId)
        socket.emit("text-selection", { text: selectedText, changes: desiredChange, documentId })
        setShowPopup(false)
        setDesiredChange("")
    }

  if (!showPopup) return null
  return (
    <div className="popup">
          <h3>Chat</h3>
          <textarea
            value={desiredChange}
            onChange={(e) => setDesiredChange(e.target.value)}
            placeholder="Ask anything"
          />
          <button onClick={handleSubmit}>Submit</button>
      <button onClick={() => setShowPopup(false)}>Cancel</button>
    </div>
  )
}

export default PopUp