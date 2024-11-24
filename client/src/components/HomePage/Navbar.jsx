import React from 'react';
import { Menu, Plus, Search, Settings } from 'lucide-react';
import { useHistory } from 'react-router-dom';
import { v4 as uuidV4 } from 'uuid';

const Navbar = () => {
  const history = useHistory();

  const createNewDocument = () => {
    history.push(`/documents/${uuidV4()}`); // Redirect to a new document with a unique ID
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-screen-xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button className="p-2 hover:bg-gray-100 rounded-full">
              <Menu className="w-6 h-6 text-gray-600" />
            </button>
            <span className="ml-4 text-gray-900 text-xl font-medium">Docs</span>
          </div>

          <div className="flex-1 max-w-2xl mx-8">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
                placeholder="Search documents"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-100 rounded-full">
              <Settings className="w-6 h-6 text-gray-600" />
            </button>
            <button onClick={createNewDocument} className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
              <Plus className="w-5 h-5" />
              <span>New</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;