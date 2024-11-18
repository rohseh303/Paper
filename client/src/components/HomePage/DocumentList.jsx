import React from 'react';
import { File, Star, Clock, Folder } from 'lucide-react';

const documents = [
  { id: 1, name: 'Project Proposal', modified: '2 days ago', starred: true },
  { id: 2, name: 'Meeting Notes', modified: '1 week ago', starred: false },
  { id: 3, name: 'Monthly Report', modified: 'Yesterday', starred: true },
  { id: 4, name: 'Team Updates', modified: '3 days ago', starred: false },
];

const DocumentList = () => {
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
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-500 cursor-pointer group transition-all"
          >
            <div className="aspect-w-8 aspect-h-11 bg-gray-50 rounded-lg mb-3 p-4 flex items-center justify-center">
              <File className="w-8 h-8 text-gray-400" />
            </div>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium text-gray-900 group-hover:text-blue-600">
                  {doc.name}
                </h3>
                <p className="text-sm text-gray-500">{doc.modified}</p>
              </div>
              {doc.starred && (
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DocumentList;