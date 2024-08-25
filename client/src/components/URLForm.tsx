import React, { useState } from 'react';

interface URLFormProps {
    onSubmit: (url: string) => void;
}

const URLForm: React.FC<URLFormProps> = ({ onSubmit }) => {
    const [url, setUrl] = useState<string>('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(url);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL"
        required
      />
      <button type="submit">Submit</button>
    </form>
  );
};

export default URLForm;
