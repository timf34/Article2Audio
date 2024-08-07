import React, { useState, useEffect } from 'react';
import { getAudioFiles, downloadFile } from '../api';

const AudioFileList = () => {
  const [audioFiles, setAudioFiles] = useState([]);

  useEffect(() => {
    const fetchAudioFiles = async () => {
      try {
        const files = await getAudioFiles();
        console.log("files", files); // "files" is an array of objects with keys "id", "file_name", and "creation_date"
        setAudioFiles(files);
      } catch (error) {
        console.error("Error fetching audio files:", error);
      }
    };
    fetchAudioFiles();
  }, []);

  const handleDownload = async (fileId) => {
    try {
      await downloadFile(fileId);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  return (
    <div>
      <h2>Audio Files</h2>
      <ul>
        {audioFiles.map((file) => (
          <li key={file.id}>
            {file.file_name} - {new Date(file.creation_date).toLocaleString()}
            <button onClick={() => handleDownload(file.id)}>Download</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AudioFileList;