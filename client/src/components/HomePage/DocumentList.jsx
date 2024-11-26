import React from 'react';
import { File, Star, Clock, Folder } from 'lucide-react';
import { io } from "socket.io-client";
import { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';

const socket = io("http://localhost:3001");

function DocumentList() {
  debugger;
  const history = useHistory();
  const [documentIds, setDocumentIds] = useState([]);

  const refreshDocuments = () => {
    socket.emit("request-document-list");
  };

  useEffect(() => {
    socket.on("document-list", (ids) => {
      setDocumentIds(ids);
    });

    // Initial request when component mounts
    refreshDocuments();

    return () => {
      socket.off("document-list");
    };
  }, []);
  debugger;

  const openDocument = (id) => {
    history.push(`/documents/${id}`); // Redirect to the selected document
  };
  debugger;

  return (
    <div className="mb-12">
      <div className="flex items-center space-x-6 mb-6">
        <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <Clock className="w-5 h-5" />
          <span>Recent</span>
        </button>
        <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <Star className="w-5 h-5" />
          <span>Starred</span>
        </button>
        <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <Folder className="w-5 h-5" />
          <span>Folders</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {documentIds.map((id) => (
          <div
            key={id}
            onClick={() => openDocument(id)}
            className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-500 cursor-pointer group transition-all"
          >
            <div className="aspect-w-8 aspect-h-11 bg-gray-50 rounded-lg mb-3 p-4 flex items-center justify-center">
              <File className="w-8 h-8 text-gray-400" />
            </div>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium text-gray-900 group-hover:text-blue-600">
                  {id}...
                </h3>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DocumentList;