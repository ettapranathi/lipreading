import React, { useState } from 'react';
import './App.css';
import VideoInputComponent from './VideoInputComponent'; // Import the VideoInputComponent
import axios from 'axios';

function App() {
  const [showOutput, setShowOutput] = useState(false);
  const [outputSentences, setOutputSentences] = useState('');
  const [accuracy, setAccuracy] = useState(0);

  const handleProcessing = async (videoFile) => {
    try {
      if (!videoFile) {
        console.error('No video file selected');
        return;
      }

      const formData = new FormData();
      formData.append('video', videoFile);
      const response = await axios.post('http://localhost:8000/process_video', formData);

      const sentences = response.data.sentences;
      const accuracy = response.data.accuracy;

      setShowOutput(true);
      setOutputSentences(sentences);
      setAccuracy(accuracy);
    } catch (error) {
      console.error('Error processing video:', error);
      setOutputSentences('Error processing video. Please try again.');
      setAccuracy(0);
    }
  };
  
  return (
    <div className='container'>
      <div className="App">
        <div className='Input'>
          <VideoInputComponent onProcess={handleProcessing}/>
        </div>
        
        {showOutput && (
          <div className='output'>
            <h2>Output</h2>
            <p>Sentences: {outputSentences}</p>
            {/* <p>Accuracy: {accuracy}</p> */}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
