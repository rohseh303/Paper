// import { useEffect, useState } from "react";
// import { useHistory } from "react-router-dom";
import { io } from "socket.io-client";
// import { v4 as uuidV4 } from "uuid";
import Navbar from "./Navbar";
import DocumentList from "./DocumentList";

// const socket = io("http://localhost:3001");

function HomePage() {
  debugger;
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-screen-xl mx-auto px-4 py-8">
        <DocumentList />
        <div className="mt-8">Hi</div>
      </main>
    </div>
  );
}

export default HomePage 