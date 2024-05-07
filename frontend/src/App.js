import React from "react";

function App() {

  const handleSearch = () => {
    const keyword = 'parking';
    fetch(`/search?q=${keyword}`)
    .then((response) => response.blob())
    .then((blob) => {
      // Create URL
      const url = window.URL.createObjectURL(blob);
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${keyword}.xlsx`); 
      document.body.appendChild(link);
      // Trigger download
      link.click();
      // Remove download link
      document.body.removeChild(link);
    });
  };
  
  return (
    <div>
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}

export default App;
