import { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { io } from "socket.io-client";
import { v4 as uuidV4 } from "uuid";

const socket = io("http://localhost:3001");

function HomePage() {
  const history = useHistory();
  const [documentIds, setDocumentIds] = useState([]);

  useEffect(() => {
    socket.on("document-list", (ids) => {
      setDocumentIds(ids); // Update state with the received document IDs
    });

    return () => {
      socket.off("document-list");
    };
  }, []);

  const openDocument = (id) => {
    history.push(`/documents/${id}`); // Redirect to the selected document
  };

  const createNewDocument = () => {
    history.push(`/documents/${uuidV4()}`); // Redirect to a new document with a unique ID
  };

  return (
    <div>
      <h1>Welcome to the Paper</h1>
      <button onClick={createNewDocument}>Create New Document</button>
      {documentIds.map((id) => (
        <button key={id} onClick={() => openDocument(id)}>
          Open Document {id}
        </button>
      ))}
    </div>
  );
}

export default HomePage 